import streamlit as st
import requests
import io
import base64
from fpdf import FPDF  

API_BASE_URL = "http://localhost:8000"

# --- Styling & Custom CSS ---
CUSTOM_CSS = """
<style>
    /* Gradient background */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(to bottom right, #1A1A1A, #2C2C2C);
        color: white;
    }

    /* Header */
    .main-title {
        font-size: 40px;
        font-weight: bold;
        text-align: center;
        color: #FFD700;
        margin-bottom: 5px;
    }

    /* Subtitle */
    .subtitle {
        font-size: 18px;
        text-align: center;
        color: #E0E0E0;
        margin-bottom: 25px;
    }

    /* YouTube Input */
    .stTextInput>div>div>input {
        background-color: #FFFFFF !important;
        color: black !important;
        font-size: 16px !important;
        padding: 10px !important;
        border-radius: 5px !important;
        border: 1px solid #FFD700 !important;
    }


    /* Buttons */
    .stButton>button {
        background-color: #FFD700;
        color: black;
        font-weight: bold;
        font-size: 16px;
        padding: 10px;
        border-radius: 8px;
        border: none;
        width: 100%;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #FFC300;
    }

    /* PDF Download Button */
    .stDownloadButton>button {
        background-color: #FF4B4B !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 16px !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px !important;
        width: 100% !important;
    }

    /* Chat Bubble */
    .chat-bubble {
        background: #2E3B4E;
        color: white;
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
        max-width: 80%;
    }
    
    .user-bubble {
        background: #FFD700;
        color: black;
        text-align: right;
        margin-left: auto;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- Dark Mode Toggle (Top Right) ---
dark_mode = st.toggle("🌙 Dark Mode", key="dark_mode_toggle", help="Switch between light and dark mode.")

# --- App Title & Branding ---
col1, col2 = st.columns([1, 5])
with col1:
    st.image("logo.jpg", width=80)  # Branding logo
with col2:
    st.markdown("<h1 class='main-title'>YouAssist: Your Own YouTube Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Don't have time to watch the whole video? We’re here to help!</p>", unsafe_allow_html=True)

# Layout: Two columns
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("### 📺 Enter YouTube URL:")
    video_url = st.text_input("YouTube URL", placeholder="Paste YouTube link here...")

    if video_url:
        if st.button("🎬 Extract Transcript"):
            payload = {"video_url": video_url}
            resp = requests.post(f"{API_BASE_URL}/extract_transcript", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                st.success("✅ Transcript extracted successfully!")
                st.session_state["transcript_text"] = data["transcript_text"]
            else:
                st.error(f"❌ Error: {resp.text}")

# --- PDF Generation Function ---
def text_to_pdf(text):
    """ Convert text to a PDF and return as bytes. """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in text.split("\n"):
        pdf.multi_cell(0, 10, line)

    buffer = io.BytesIO()
    pdf.output(dest="S").encode("latin1")  
    buffer.write(pdf.output(dest="S").encode("latin1"))  
    buffer.seek(0)  #  Move pointer to the beginning

    pdf_bytes = buffer.getvalue()
    print(f"DEBUG - Generated PDF Size: {len(pdf_bytes)} bytes")  # ✅Debugging output

    return pdf_bytes


# --- Show Download Buttons If Transcript Exists ---
if "transcript_text" in st.session_state:
    transcript_text = st.session_state["transcript_text"]

    pdf_data = text_to_pdf(transcript_text)  # ✅ Calling the function here
    st.download_button("📄 Download Transcript as PDF", pdf_data, "transcript.pdf", "application/pdf")  

    if st.button("📑 Summarize Transcript"):
        with st.spinner("⏳ Generating summary..."):
            payload = {"transcript_text": transcript_text}
            resp = requests.post(f"{API_BASE_URL}/summarize", json=payload)
            if resp.status_code == 200:
                summary = resp.json()["summary"]
                st.session_state["summary_text"] = summary
                st.success("✅ Summary Ready!")

    if "summary_text" in st.session_state:
        summary_text = st.session_state["summary_text"]
        summary_pdf = text_to_pdf(summary_text)
        st.download_button("📜 Download Summary as PDF", summary_pdf, "summary.pdf", "application/pdf")

# Branding Image
with col2:
    st.image("logo.jpg", use_container_width=True)

# --- Chat Section ---
st.markdown("## 💬 Chat with YouAssist")
st.write("Ask anything about the video transcript!")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

user_query = st.text_input("💡 Type your question here...")

if user_query:
    with st.spinner("🤖 Thinking..."):
        payload = {"user_query": user_query}
        resp = requests.post(f"{API_BASE_URL}/chat", json=payload)
        if resp.status_code == 200:
            answer = resp.json()["answer"]
            st.session_state["chat_history"].append(("user", user_query))
            st.session_state["chat_history"].append(("bot", answer))
        else:
            st.error("❌ Error fetching response!")

# Display chat messages with formatting
for role, message in st.session_state["chat_history"]:
    bubble_class = "chat-bubble"
    if role == "user":
        bubble_class += " user-bubble"
    st.markdown(f"<div class='{bubble_class}'>{message}</div>", unsafe_allow_html=True)
