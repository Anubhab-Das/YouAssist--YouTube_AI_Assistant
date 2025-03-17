import openai
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
from langgraph.graph import StateGraph
from pydantic import BaseModel
import os
from chromadb import PersistentClient
from llm_guard.input_scanners import (
    PromptInjection, BanSubstrings, Toxicity as InputToxicity, Regex, Language
)
from llm_guard.output_scanners import (
    Toxicity as OutputToxicity, Bias, MaliciousURLs, NoRefusal
)
from llm_guard.output_scanners.toxicity import MatchType  # ✅ FIXED IMPORT

DEFAULT_MODEL = "gpt-4o-mini"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "<YOUR_OPENAI_API_KEY>")

client = OpenAI(api_key=OPENAI_API_KEY)

class RAGState(BaseModel):
    transcript_text: str = ""
    user_query: str = ""
    summary: str = ""
    answer: str = ""

def get_embedding(text: str, engine: str = "text-embedding-ada-002") -> list:
    """ Retrieves an embedding for the given text. """
    response = client.embeddings.create(model=engine, input=text)
    return response.data[0].embedding

class RAGPipeline:
    def __init__(self, openai_api_key: str):
        openai.api_key = openai_api_key
        self.chroma_client = PersistentClient(path=".chroma_db")
        self.collection = self.chroma_client.get_or_create_collection("transcript_chunks")
        self.workflow = self._create_pipeline()

    def _create_pipeline(self):
        workflow = StateGraph(state_schema=RAGState)
        workflow.add_node("summarize_node", self._summarize_node)
        workflow.add_node("chat_node", self._chat_node)
        workflow.set_entry_point("summarize_node")
        workflow.add_edge("summarize_node", "chat_node")
        workflow.set_finish_point("chat_node")
        return workflow.compile()

    def ingest_transcript(self, transcript_text: str):
        """ Splits transcript, generates embeddings, and stores them in ChromaDB. """
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_text(transcript_text)

        existing_ids = set(self.collection.get()["ids"])
        for idx, chunk in enumerate(chunks):
            doc_id = f"transcript-chunk-{idx}"

            if doc_id in existing_ids:
                print(f"⚠️ Skipping duplicate embedding: {doc_id}")
                continue  

            embedding_vector = get_embedding(chunk, engine="text-embedding-ada-002")
            self.collection.add(
                documents=[chunk],
                metadatas=[{"chunk_index": idx}],
                embeddings=[embedding_vector],
                ids=[doc_id]
            )

    def summarize_transcript(self, transcript_text: str) -> str:
        """ Generates a concise summary using LLM. """
        state = RAGState(transcript_text=transcript_text)
        updated_state = self.workflow.invoke(state)
        return updated_state.get("summary", "Summary generation failed")

    def _summarize_node(self, state: RAGState) -> dict:
        """ Generates summary using OpenAI. """
        prompt = f"Summarize the following transcript:\n\n{state.transcript_text}"
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "Generate a concise summary of the given transcript."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        return {"summary": response.choices[0].message.content.strip()}

    def chat_with_transcript(self, user_query: str) -> str:
        """Fetches similar transcript chunks and generates a response."""

        input_scanners = [
            PromptInjection(),  
            BanSubstrings(["hack", "leak", "cheat"]),  
            InputToxicity(),  
            Regex(patterns=[r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"]),  
            Language(["en"]),  
        ]

        for scanner in input_scanners:
            try:
                print(f"🔍 Running scanner: {scanner.__class__.__name__}")  
                sanitized_input, is_valid, risk_score = scanner.scan(user_query)
                if not is_valid:
                    return f"🚨 Restricted content detected by {scanner.__class__.__name__}. Try rephrasing."
            except Exception as e:
                print(f"❌ Scanner {scanner.__class__.__name__} failed: {e}")
                return f"⚠️ Security scanner error: {scanner.__class__.__name__}"

        state = RAGState(user_query=user_query)
        updated_state = self.workflow.invoke(state)
        response = updated_state.get("answer", "Chatbot failed to generate a response.")

        # ✅ **Enhanced Output Filtering with LLM Guard**
        output_scanners = [
            OutputToxicity(threshold=0.5, match_type=MatchType.SENTENCE),  
            Bias(),  
            MaliciousURLs(),  
            NoRefusal()  
        ]

        for scanner in output_scanners:
            try:
                print(f"🔍 Running scanner: {scanner.__class__.__name__}")  

                # ✅ **Fixed `scan()` method to include both `prompt` and `output`**
                sanitized_output, is_valid, risk_score = scanner.scan(prompt=user_query, output=response)

                if not is_valid:
                    return f"⚠️ Response blocked by {scanner.__class__.__name__} due to security concerns."
            except Exception as e:
                print(f"❌ Scanner {scanner.__class__.__name__} failed: {e}")
                return f"⚠️ Security scanner error: {scanner.__class__.__name__}"

        return sanitized_output  

    def _chat_node(self, state: RAGState) -> dict:
        """ Retrieves context from ChromaDB and generates a response. """
        query_embedding = get_embedding(state.user_query, engine="text-embedding-ada-002")
        results = self.collection.query(query_embeddings=[query_embedding], n_results=3)
        retrieved_chunks = results["documents"][0] if results.get("documents") else []

        if not retrieved_chunks:
            return {"answer": "No relevant transcript data found. Try re-extracting the transcript."}

        context_text = "\n\n".join(retrieved_chunks)
        system_message = f"Answer the user's question using the transcript context below:\n\n{context_text}\n\n"

        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": state.user_query}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return {"answer": response.choices[0].message.content.strip()}

# Write a function to clean and normalize text
