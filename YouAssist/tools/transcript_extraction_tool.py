# tools/transcript_extraction_tool.py

import os
import openai
from fastapi import HTTPException
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube

from .base_tool import BaseTool
from rag import RAGPipeline

def extract_video_id(url: str) -> str:
    """
    Extract the 'v' parameter from a YouTube URL.
    Raise ValueError if not found.
    """
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)
    video_id_list = query.get("v")
    if video_id_list:
        return video_id_list[0]
    raise ValueError("Invalid YouTube URL. Could not extract video ID.")

class TranscriptExtractionTool(BaseTool):
    """
    Extract the full transcript from YouTube using YouTubeTranscriptApi,
    then ingest it into the RAG pipeline.
    """
    def __init__(self, rag_pipeline: RAGPipeline):
        self.rag_pipeline = rag_pipeline

    def run(self, video_url: str) -> str:
        """
        1) Extract the video ID from the URL.
        2) Fetch the full transcript using YouTubeTranscriptApi.
        3) Ingest the transcript into the RAG pipeline.
        4) Return the full transcript text.
        """
        try:
            video_id = extract_video_id(video_url)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        try:
            full_transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = " ".join(seg["text"] for seg in full_transcript)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        self.rag_pipeline.ingest_transcript(transcript_text)
        return transcript_text
