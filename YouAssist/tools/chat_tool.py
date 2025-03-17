# tools/chat_tool.py

from fastapi import HTTPException
from .base_tool import BaseTool
from rag import RAGPipeline

class ChatTool(BaseTool):
    """
    Chat with the user using context from the RAG pipeline.
    """
    def __init__(self, rag_pipeline: RAGPipeline):
        self.rag_pipeline = rag_pipeline

    def run(self, user_query: str) -> str:
        try:
            return self.rag_pipeline.chat_with_transcript(user_query)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
