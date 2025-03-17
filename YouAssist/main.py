import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from tools.transcript_extraction_tool import TranscriptExtractionTool
from tools.summarize_tool import SummarizeTool
from tools.chat_tool import ChatTool
from rag import RAGPipeline

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "<YOUR_OPENAI_API_KEY>")
rag_pipeline = RAGPipeline(openai_api_key=OPENAI_API_KEY)

app = FastAPI()

class TranscriptRequest(BaseModel):
    video_url: str

class SummarizeRequest(BaseModel):
    transcript_text: str

class ChatRequest(BaseModel):
    user_query: str

@app.post("/extract_transcript")
def extract_transcript(request: TranscriptRequest):
    tool = TranscriptExtractionTool(rag_pipeline)
    transcript_text = tool.run(video_url=request.video_url)
    return {"transcript_text": transcript_text}

@app.post("/summarize")
def summarize_text(request: SummarizeRequest):
    return {"summary": rag_pipeline.summarize_transcript(request.transcript_text)}

@app.post("/chat")
def chat_with_agent(request: ChatRequest):
    return {"answer": rag_pipeline.chat_with_transcript(request.user_query)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
