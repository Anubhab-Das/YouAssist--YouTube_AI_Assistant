# YouAssist - Your Own YouTube Assistant 🎥🤖



## 🚀 Overview

**YouAssist** is a YouTube transcript summarization and chat assistant powered by LLMs. It allows users to extract, summarize, and interact with video transcripts, providing concise insights without watching the full video. Incorporated with LLM-Guard to ensure secure end-to-end usage.

🔹 Extracts video transcripts based on custom start time and duration.  
🔹 Summarizes transcripts using OpenAI. 
🔹 Supports a Retrieval-Augmented Generation (RAG) chatbot for interactive Q&A.  
🔹 Embeds transcripts using OpenAI embeddings and stores them in **ChromaDB**.  
🔹 Offers a **FastAPI backend** and a **Streamlit UI** for seamless interaction.  

## 🛠️ Features

- 🎯 **YouTube Transcript Extraction** – Fetches transcripts using `youtube-transcript-api`.
- 📄 **Download Transcript** – Save transcripts as a PDF for offline reading.
- ✍️ **Summarization** – Generates concise summaries using OpenAI/Gemini models.
- 🗃 **RAG-Powered Chatbot** – Enables interactive Q&A using ChromaDB for contextual search.
- ⚡ **Optimized Performance** – Includes caching, security scanning, and efficient chunking.
- 🎨 **User-Friendly UI** – Styled with a dark mode toggle, animations, and a clean layout.

## 📂 Project Structure

```
YouGPT/
│── api.py                      # FastAPI endpoints for summarization & chatbot
│── app.py                      # Streamlit frontend for user interaction
│── base_tool.py                # Abstract base class for tools
│── chat_tool.py                # Chatbot agent implementation
│── summarize_tool.py           # Summarization logic
│── transcript_extraction_tool.py # Extracts transcripts from YouTube
│── tool_registry.py            # Registers all tools
│── rag.py                      # RAG pipeline for chatbot retrieval
│── main.py                     # Entry point for running the API
│── requirements.txt            # Dependencies
│── assets/                     # Logos & branding images
│── output/                     # Stores generated transcripts/summaries
│── templates/                  # PPT templates (if needed)
│── uploads/                    # Uploaded files (PDFs, videos, etc.)
```

## 🚀 Quick Start

### 1️⃣ Clone the Repository


### 2️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

### 3️⃣ Run FastAPI Backend
```sh
uvicorn app:app --reload
```

### 4️⃣ Run Streamlit Frontend
```sh
streamlit run app.py
```

## 🏗️ Tech Stack
- **Backend:** FastAPI, LangGraph, OpenAI API, Gemini API
- **Frontend:** Streamlit
- **Database:** ChromaDB (for transcript embeddings)
- **LLMs:** OpenAI GPT-4o, Gemini, Local Ollama Models

## 🛡️ Security & Performance Optimizations
- **🛠 Async Processing:** Uses `asyncio.gather()` for efficiency.
- **🛡 LLM Guard:** Scans user input/output for harmful content.
- **📌 Caching:** Avoids redundant API calls using `lru_cache()`.

## Sample Output:

![Screenshot 2025-03-17 at 3 05 45 PM](https://github.com/user-attachments/assets/116cf17a-9e58-400a-beb8-90a9786a9607)


## 🔥 Future Enhancements
✅ Integrate speech-to-text for non-captioned videos.  
✅ Add multi-language support for transcripts.  
✅ Enable custom model selection for chatbot responses.  

---

⭐ **If you find this project useful, don't forget to give it a star!** ⭐

