# BharatLearn AI - Enhanced with LangChain + ChromaDB
# Multilingual Learning Assistant with RAG Pipeline

import streamlit as st
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from PyPDF2 import PdfReader
from gtts import gTTS
import tempfile

# LangChain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

LANGUAGES = {
    "English": "en",
    "Hindi": "hi", 
    "Marathi": "mr",
    "Tamil": "ta",
    "Telugu": "te"
}

# Extract PDF with page numbers
def extract_and_chunk_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    full_text = ""
    chunks_with_metadata = []
    
    for page_num, page in enumerate(pdf_reader.pages, start=1):
        page_text = page.extract_text()
        full_text += page_text
        
        # Split page into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        page_chunks = text_splitter.split_text(page_text)
        
        # Add page number to each chunk
        for chunk in page_chunks:
            chunks_with_metadata.append({
                "text": chunk,
                "page": page_num
            })
    
    return full_text, chunks_with_metadata

# Create ChromaDB vector store
def create_vector_store(chunks_with_metadata):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=GOOGLE_API_KEY
    )
    
    texts = [chunk["text"] for chunk in chunks_with_metadata]
    metadatas = [{"page": chunk["page"]} for chunk in chunks_with_metadata]
    
    vector_store = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas
    )
    
    return vector_store

# Q&A with page number citations - Returns clean text
def ask_question_langchain(question, vector_store, language):
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.7
    )
    
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    relevant_docs = retriever.invoke(question)
    
    context = "\n\n".join([doc.page_content for doc in relevant_docs])
    page_numbers = [doc.metadata.get("page", "Unknown") for doc in relevant_docs]
    
    prompt = f"""You are a helpful educational assistant. Answer the question based on the context provided.

Context from the document:
{context}

Question: {question}

Instructions:
- Answer in {language}
- Write naturally in paragraphs like a teacher explaining
- DO NOT use JSON format
- DO NOT use structured lists unless necessary
- Be conversational and clear
- If the answer is not in the context, say "I cannot find this information in the document"
- Mention that the information is from pages {page_numbers}

Provide a clear, natural answer:"""
    
    response = llm.invoke(prompt)
    
    return response.content, relevant_docs

# Generate MCQs - Simple text format that works
def create_mcqs_json(pdf_text, language):
    model = genai.GenerativeModel('gemini-flash-latest')
    
    prompt = f"""Create 10 multiple choice questions from this text in {language}.

Text: {pdf_text[:3000]}

Format each question EXACTLY like this:
Q1: What is photosynthesis?
A) Process of eating
B) Process of making food
C) Process of breathing
D) Process of sleeping
Correct Answer: B

Q2: Where does photosynthesis occur?
A) Roots
B) Stem
C) Leaves
D) Flowers
Correct Answer: C

Now create 10 questions following this EXACT format:"""
    
    try:
        response = model.generate_content(prompt)
        mcqs = parse_mcq_text_to_json(response.text)
        if len(mcqs) > 0:
            return mcqs
        else:
            st.error("Could not parse MCQs. Please try again.")
            return []
    except Exception as e:
        st.error(f"MCQ generation error: {str(e)}")
        return []

# Fallback parser
def parse_mcq_text_to_json(text):
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
                    "correct_answer": current_ans,
                    "explanation": ""
                })
            current_q = line.split(':', 1)[1].strip()
            current_opts = []
            current_ans = None
        
        elif line.startswith(('A)', 'B)', 'C)', 'D)')):
            current_opts.append(line)
        
        elif 'Answer:' in line:
            ans = line.split(':')[-1].strip().upper()
            if ans in ['A', 'B', 'C', 'D']:
                current_ans = ans
    
    if current_q and len(current_opts) == 4 and current_ans:
        questions.append({
            "question": current_q,
            "options": current_opts,
            "correct_answer": current_ans,
            "explanation": ""
        })
    
    return questions[:10]

# Audio summary - Fixed version
def create_audio_summary(pdf_text, language):
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = f"""Create a clear 250-word summary in {language} suitable for audio listening.

Text: {pdf_text[:4000]}

Write a natural, flowing summary:"""
        
        response = model.generate_content(prompt)
        summary = response.text
        
        # Get language code
        lang_code = LANGUAGES.get(language, "en")
        
        # Create audio
        tts = gTTS(text=summary, lang=lang_code, slow=False)
        
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_filename = temp_file.name
        temp_file.close()  # Close before saving
        
        tts.save(temp_filename)
        
        # Read audio bytes
        with open(temp_filename, "rb") as f:
            audio_bytes = f.read()
        
        # Clean up temp file
        try:
            os.unlink(temp_filename)
        except:
            pass
        
        return audio_bytes, summary
        
    except Exception as e:
        st.error(f"Audio generation error: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None, None

# Streamlit UI
st.set_page_config(
    page_title="BharatLearn AI",
    page_icon=":books:",
    layout="wide"
)

st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    h1 { color: #2c3e50; font-weight: 700; }
    .stButton>button {
        background-color: #2c3e50;
        color: white;
        border-radius: 6px;
        padding: 0.6rem 1.2rem;
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

st.title("BharatLearn AI")
st.markdown("**Powered by LangChain + ChromaDB + Google Gemini**")
st.markdown("---")

if not GOOGLE_API_KEY:
    st.error("Add GOOGLE_API_KEY to .env file")
    st.stop()

# Session state
if 'pdf_text' not in st.session_state:
    st.session_state.pdf_text = None
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
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
            with st.spinner("Processing with ChromaDB..."):
                try:
                    text, chunks = extract_and_chunk_pdf(pdf_file)
                    st.session_state.pdf_text = text
                    st.session_state.vector_store = create_vector_store(chunks)
                    st.success(f"Processed! {len(chunks)} chunks created")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    st.divider()
    
    st.header("Language")
    language = st.selectbox("Choose language", list(LANGUAGES.keys()))
    
    st.divider()
    
    st.header("Studio")
    
    if st.session_state.pdf_text:
        if st.button("Generate MCQs (JSON)"):
            with st.spinner("Creating JSON MCQs..."):
                try:
                    mcqs = create_mcqs_json(st.session_state.pdf_text, language)
                    st.session_state.mcqs = mcqs
                    st.success(f"{len(mcqs)} questions created!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        if st.button("Generate Audio"):
            with st.spinner("Creating audio..."):
                try:
                    audio, text = create_audio_summary(st.session_state.pdf_text, language)
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
if st.session_state.vector_store:
    st.header("Ask Questions")
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "sources" in msg and msg["sources"]:
                with st.expander("View Sources with Page Numbers"):
                    for i, source in enumerate(msg["sources"], 1):
                        page_num = source.metadata.get("page", "Unknown")
                        st.caption(f"**Page {page_num}:** {source.page_content[:200]}...")
    
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
                    answer, sources = ask_question_langchain(
                        question,
                        st.session_state.vector_store,
                        language
                    )
                    
                    st.write(answer)
                    
                    if sources:
                        with st.expander("View Sources with Page Numbers"):
                            for i, source in enumerate(sources, 1):
                                page_num = source.metadata.get("page", "Unknown")
                                st.caption(f"**Page {page_num}:** {source.page_content[:200]}...")
                    
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                except Exception as e:
                    st.error(f"Error: {e}")
    
    if st.session_state.mcqs:
        st.divider()
        st.header("Practice Questions (JSON Format)")
        
        for i, mcq in enumerate(st.session_state.mcqs, 1):
            with st.expander(f"Q{i}: {mcq['question'][:50]}..."):
                st.write(f"**{mcq['question']}**")
                st.write("")
                for opt in mcq['options']:
                    st.write(opt)
                st.write("")
                st.info(f"Correct Answer: {mcq['correct_answer']}")
                if mcq.get('explanation'):
                    st.caption(f"Explanation: {mcq['explanation']}")

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
    
    # Getting started box
    st.markdown("""
    <div class="info-box">
        <strong>Getting Started:</strong> Upload a PDF document from the sidebar to begin.
    </div>
    """, unsafe_allow_html=True)
