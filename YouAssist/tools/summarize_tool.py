# tools/summarize_tool.py

from fastapi import HTTPException
from .base_tool import BaseTool
from rag import RAGPipeline

class SummarizeTool(BaseTool):
    """
    Summarize a given transcript text using the RAG pipeline.
    """
    def __init__(self, rag_pipeline: RAGPipeline):
        self.rag_pipeline = rag_pipeline

    def run(self, transcript_text: str) -> str:
        try:
            return self.rag_pipeline.summarize_transcript(transcript_text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
