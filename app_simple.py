"""
BharatLearn AI - Simple & Clean Version
No complex dependencies - just works!
"""

import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PyPDF2 import PdfReader
from gtts import gTTS
import tempfile

# Load environment
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Languages
LANGUAGES = {
    "English": "en",
    "Hindi": "hi", 
    "Marathi": "mr",
    "Tamil": "ta",
    "Telugu": "te"
}

# Extract PDF text
def extract_pdf_text(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Ask question
def ask_question(question, pdf_text, language):
    model = genai.GenerativeModel('gemini-flash-latest')
    
    prompt = f"""Answer based ONLY on the context below.

Context: {pdf_text[:5000]}

Question: {question}

Answer in {language}. If not in context, say "I cannot find this information."

Answer:"""
    
    response = model.generate_content(prompt)
    return response.text

# Generate MCQs
def create_mcqs(pdf_text, language):
    model = genai.GenerativeModel('gemini-flash-latest')
    
    prompt = f"""Create 10 MCQs in {language}.

Text: {pdf_text[:3000]}

Format EXACTLY:
Q1: [question]
A) [option]
B) [option]
C) [option]
D) [option]
Correct Answer: A

Create all 10:"""
    
    response = model.generate_content(prompt)
    return parse_mcqs(response.text)

# Parse MCQs
def parse_mcqs(text):
    questions = []
    lines = text.split('\n')
    current_q = None
    current_opts = []
    current_ans = None
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('Q') and ':' in line:
            if current_q and len(current_opts) == 4 and current_ans:
                questions.append({
                    "question": current_q,
                    "options": current_opts,
                    "answer": current_ans
                })
            current_q = line.split(':', 1)[1].strip()
            current_opts = []
            current_ans = None
        
        elif line.startswith(('A)', 'B)', 'C)', 'D)')):
            current_opts.append(line[2:].strip())
        
        elif 'Answer:' in line:
            ans = line.split(':')[-1].strip().upper()
            if ans in ['A', 'B', 'C', 'D']:
                current_ans = ans
    
    if current_q and len(current_opts) == 4 and current_ans:
        questions.append({
            "question": current_q,
            "options": current_opts,
            "answer": current_ans
        })
    
    return questions[:10]

# Create audio
def create_audio(pdf_text, language):
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = f"""Summarize in 250 words in {language}. Audio-friendly.

Text: {pdf_text[:4000]}

Summary:"""
        
        response = model.generate_content(prompt)
        summary = response.text
        
        lang_code = LANGUAGES[language]
        tts = gTTS(text=summary, lang=lang_code, slow=False)
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_name = temp_file.name
        temp_file.close()
        
        tts.save(temp_name)
        
        with open(temp_name, "rb") as f:
            audio_bytes = f.read()
        
        os.unlink(temp_name)
        
        return audio_bytes, summary
    except Exception as e:
        st.error(f"Audio error: {str(e)}")
        return None, None

# Page config
st.set_page_config(
    page_title="BharatLearn AI",
    page_icon=":books:",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    .main { 
        background-color: #f8f9fa;
    }
    h1 { 
        color: #2c3e50;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .stButton>button {
        background-color: #2c3e50;
        color: white;
        border-radius: 6px;
        padding: 0.6rem 1.2rem;
        border: none;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton>button:hover { 
        background-color: #34495e;
    }
    .feature-box {
        background: white;
        padding: 2rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        height: 100%;
    }
    .feature-box h3 {
        color: #2c3e50;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }
    .feature-box p {
        color: #5a6c7d;
        line-height: 1.6;
        margin: 0;
    }
    .info-box {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #2c3e50;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("BharatLearn AI")
st.markdown("**Multilingual Learning Assistant**")
st.markdown("---")

# Check API key
if not GOOGLE_API_KEY:
    st.error("WARNING: Add GOOGLE_API_KEY to .env file")
    st.info("Get key: https://makersuite.google.com/app/apikey")
    st.stop()

# Session state
if 'pdf_text' not in st.session_state:
    st.session_state.pdf_text = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'mcqs' not in st.session_state:
    st.session_state.mcqs = None
if 'audio' not in st.session_state:
    st.session_state.audio = None
if 'audio_text' not in st.session_state:
    st.session_state.audio_text = None

# Sidebar
with st.sidebar:
    st.header("Upload PDF")
    
    pdf_file = st.file_uploader("Choose PDF", type="pdf")
    
    if pdf_file:
        if st.button("Process PDF"):
            with st.spinner("Processing..."):
                try:
                    text = extract_pdf_text(pdf_file)
                    st.session_state.pdf_text = text
                    st.success(f"Processed! ({len(text)} chars)")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    st.divider()
    
    st.header("Language")
    language = st.selectbox("Choose language", list(LANGUAGES.keys()))
    
    st.divider()
    
    st.header("Studio")
    
    if st.session_state.pdf_text:
        if st.button("Generate MCQs"):
            with st.spinner("Creating..."):
                try:
                    mcqs = create_mcqs(st.session_state.pdf_text, language)
                    st.session_state.mcqs = mcqs
                    st.success(f"{len(mcqs)} questions created!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        if st.button("Generate Audio"):
            with st.spinner("Creating..."):
                try:
                    audio, text = create_audio(st.session_state.pdf_text, language)
                    if audio:
                        st.session_state.audio = audio
                        st.session_state.audio_text = text
                        st.success("Audio ready!")
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.info("Upload PDF first")
    
    st.divider()
    
    if st.session_state.audio:
        st.subheader("Audio Summary")
        st.audio(st.session_state.audio, format="audio/mp3")
        if st.session_state.audio_text:
            with st.expander("View Text"):
                st.write(st.session_state.audio_text)

# Main area
if st.session_state.pdf_text:
    st.header("Ask Questions")
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    question = st.chat_input("Ask about your PDF...")
    
    if question:
        with st.chat_message("user"):
            st.write(question)
        
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer = ask_question(
                        question,
                        st.session_state.pdf_text,
                        language
                    )
                    st.write(answer)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer
                    })
                except Exception as e:
                    st.error(f"Error: {e}")
    
    if st.session_state.mcqs:
        st.divider()
        st.header("Practice Questions")
        
        for i, mcq in enumerate(st.session_state.mcqs, 1):
            with st.expander(f"Q{i}: {mcq['question'][:50]}..."):
                st.write(f"**{mcq['question']}**")
                st.write("")
                for j, opt in enumerate(mcq['options']):
                    st.write(f"{chr(65+j)}) {opt}")
                st.write("")
                st.info(f"Correct Answer: {mcq['answer']}")

else:
    # Professional Landing Page
    st.markdown("### Welcome to BharatLearn AI")
    st.markdown("An intelligent platform for multilingual learning from PDF documents.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Feature boxes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-box">
            <h3>PDF Analysis</h3>
            <p>Upload educational PDFs and get instant access to intelligent question-answering powered by AI.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-box">
            <h3>Multilingual Support</h3>
            <p>Learn in English, Hindi, Tamil, Telugu, or Marathi. Choose your preferred language.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-box">
            <h3>Practice Tools</h3>
            <p>Generate MCQs for practice and audio summaries for efficient revision.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Getting started
    st.markdown("""
    <div class="info-box">
        <strong>Getting Started:</strong> Upload a PDF document from the sidebar to begin.
    </div>
    """, unsafe_allow_html=True)
