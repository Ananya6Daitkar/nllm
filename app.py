
#BharatLearn AI - Multilingual Learning Assistant



# importing all the libraries
import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PyPDF2 import PdfReader
from gtts import gTTS
import tempfile

# load environment variables from .env file
load_dotenv()

# get the Google API key from environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# configure Google Gemini AI with the API key
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# define the supported languages with their codes
LANGUAGES = {
    "English": "en",
    "Hindi": "hi", 
    "Marathi": "mr",
    "Tamil": "ta",
    "Telugu": "te"
}

# extracting text from pdf file
def extract_pdf_text(pdf_file):
    """
    This function reads a PDF file and extracts all the text from it
    """
    # create a PDF reader object
    pdf_reader = PdfReader(pdf_file)
    
    # initialize empty string to store text
    text = ""
    
    # loop through all pages and extract text
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    # return the extracted text
    return text

# asking question to AI based on PDF content
def ask_question(question, pdf_text, language):
    """
    This function sends a question to AI and gets an answer based on PDF content
    """
    # create the Gemini AI model
    model = genai.GenerativeModel('gemini-flash-latest')
    
    # create the prompt with context and question
    prompt = f"""You are a helpful educational assistant. Answer the question based ONLY on the provided context.

Context from PDF:
{pdf_text[:5000]}

Question: {question}

Instructions:
- Answer in {language}
- If the answer is not in the context, say "I cannot find this information in the document."
- Be clear and educational

Answer:"""
    
    # generate the response from AI
    response = model.generate_content(prompt)
    
    # return the answer text
    return response.text

# generating MCQs from PDF content
def create_mcqs(pdf_text, language):
    """
    This function generates 10 multiple choice questions from the PDF content
    """
    # create the Gemini AI model
    model = genai.GenerativeModel('gemini-flash-latest')
    
    # use only first 3000 characters to avoid token limits
    short_text = pdf_text[:3000]
    
    # create the prompt for MCQ generation
    prompt = f"""Create 10 multiple choice questions from this text in {language}.

Text:
{short_text}

Format each question exactly like this:
Q1: [Question text here]
A) [First option]
B) [Second option]
C) [Third option]
D) [Fourth option]
Correct Answer: A

Create all 10 questions now:"""
    
    # generate the MCQs from AI
    response = model.generate_content(prompt)
    
    # parse the response text into structured format
    return parse_mcq_text(response.text)

# parsing MCQ text into structured format
def parse_mcq_text(text):
    """
    This function converts the MCQ text into a list of question dictionaries
    """
    # initialize empty list to store questions
    questions = []
    
    # split the text into lines
    lines = text.split('\n')
    
    # initialize variables to track current question
    current_question = None
    current_options = []
    current_answer = None
    
    # loop through each line
    for line in lines:
        # remove extra spaces
        line = line.strip()
        
        # check if line starts with Q (question line)
        if line.startswith('Q') and ':' in line:
            # save the previous question if it's complete
            if current_question and len(current_options) == 4 and current_answer:
                questions.append({
                    "question": current_question,
                    "options": current_options,
                    "answer": current_answer
                })
            
            # start a new question
            current_question = line.split(':', 1)[1].strip()
            current_options = []
            current_answer = None
        
        # check if line starts with A), B), C), or D) (option line)
        elif line.startswith(('A)', 'B)', 'C)', 'D)')):
            # extract the option text
            option = line[2:].strip()
            current_options.append(option)
        
        # check if line contains the correct answer
        elif 'Answer:' in line:
            # extract the answer letter
            answer = line.split(':')[-1].strip().upper()
            if answer in ['A', 'B', 'C', 'D']:
                current_answer = answer
    
    # save the last question
    if current_question and len(current_options) == 4 and current_answer:
        questions.append({
            "question": current_question,
            "options": current_options,
            "answer": current_answer
        })
    
    # return maximum 10 questions
    return questions[:10]

# generating audio summary of PDF
def create_audio_summary(pdf_text, language):
    """
    This function creates an audio summary of the PDF content
    """
    try:
        # create the Gemini AI model
        model = genai.GenerativeModel('gemini-flash-latest')
        
        # use only first 4000 characters
        short_text = pdf_text[:4000]
        
        # create the prompt for summary generation
        prompt = f"""Summarize this text in 250 words in {language}. Make it suitable for audio listening.

Text:
{short_text}

Summary:"""
        
        # generate the summary from AI
        response = model.generate_content(prompt)
        summary = response.text
        
        # get the language code for text-to-speech
        lang_code = LANGUAGES[language]
        
        # create text-to-speech object
        tts = gTTS(text=summary, lang=lang_code, slow=False)
        
        # create a temporary file to save audio - FIXED VERSION
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_filename = temp_file.name
        temp_file.close()  # Close file before saving
        
        # save the audio to temporary file
        tts.save(temp_filename)
        
        # read the audio file as bytes
        with open(temp_filename, "rb") as f:
            audio_bytes = f.read()
        
        # delete the temporary file
        os.unlink(temp_filename)
        
        # return the audio bytes and summary
        return audio_bytes, summary
    
    except Exception as e:
        st.error(f"Audio error: {str(e)}")
        return None, None

# Streamlit page configuration
st.set_page_config(
    page_title="BharatLearn AI",
    page_icon="book",
    layout="wide"
)

# custom CSS for styling
st.markdown("""
<style>
    .main {
        background-color: #ffffff;
    }
    h1 {
        color: #1a73e8;
        font-weight: 400;
    }
    .stButton>button {
        background-color: #1a73e8;
        color: white;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1557b0;
    }
</style>
""", unsafe_allow_html=True)

# main title
st.title("BharatLearn AI")
st.write("Your Multilingual Learning Assistant")

# check if API key is configured
if not GOOGLE_API_KEY:
    st.error("Please add GOOGLE_API_KEY to your .env file")
    st.info("Get your free API key from: https://makersuite.google.com/app/apikey")
    st.stop()

# initialize session state variables to store data across reruns
if 'pdf_text' not in st.session_state:
    st.session_state.pdf_text = None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'mcqs' not in st.session_state:
    st.session_state.mcqs = None

if 'audio' not in st.session_state:
    st.session_state.audio = None

if 'audio_summary_text' not in st.session_state:
    st.session_state.audio_summary_text = None

# sidebar for PDF upload and settings
with st.sidebar:
    # PDF upload section
    st.header("Upload PDF")
    
    # file uploader widget
    pdf_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    # process PDF button
    if pdf_file:
        if st.button("Process PDF"):
            # show loading spinner
            with st.spinner("Reading PDF..."):
                try:
                    # extract text from PDF
                    text = extract_pdf_text(pdf_file)
                    
                    # store text in session state
                    st.session_state.pdf_text = text
                    
                    # show success message
                    st.success(f"PDF processed successfully! ({len(text)} characters)")
                except Exception as e:
                    # show error message if something goes wrong
                    st.error(f"Error: {e}")
    
    # divider line
    st.divider()
    
    # language selection section
    st.header("Language")
    language = st.selectbox(
        "Choose your language",
        list(LANGUAGES.keys())
    )
    
    # divider line
    st.divider()
    
    # studio features section
    st.header("Studio")
    
    # check if PDF is uploaded
    if st.session_state.pdf_text:
        # MCQ generation button
        if st.button("Generate MCQs"):
            with st.spinner("Creating questions..."):
                try:
                    # generate MCQs
                    mcqs = create_mcqs(st.session_state.pdf_text, language)
                    
                    # store MCQs in session state
                    st.session_state.mcqs = mcqs
                    
                    # show success message
                    st.success(f"Generated {len(mcqs)} questions successfully!")
                except Exception as e:
                    # show error message
                    st.error(f"Error: {e}")
        
        # audio summary button
        if st.button("🔊 Generate Audio Summary"):
            with st.spinner("Creating audio..."):
                try:
                    # generate audio summary
                    audio, summary_text = create_audio_summary(st.session_state.pdf_text, language)
                    
                    if audio:
                        # store audio in session state so it persists
                        st.session_state.audio = audio
                        st.session_state.audio_summary_text = summary_text
                        
                        # show success message
                        st.success("✅ Audio summary created!")
                    else:
                        st.error("❌ Failed to create audio")
                except Exception as e:
                    # show error message
                    st.error(f"❌ Error: {e}")
    else:
        # show info message if no PDF uploaded
        st.info("📤 Please upload and process a PDF first")
    
    # divider
    st.divider()
    
    # display audio player if audio exists
    if st.session_state.audio:
        st.subheader("🎧 Audio Summary")
        st.audio(st.session_state.audio, format="audio/mp3")
        
        # show summary text in expander
        if st.session_state.audio_summary_text:
            with st.expander("📄 View Summary Text"):
                st.write(st.session_state.audio_summary_text)

# main content area
# check if PDF is uploaded
if st.session_state.pdf_text:
    # chat section header
    st.header("Ask Questions")
    
    # display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # chat input box
    question = st.chat_input("Ask a question about your PDF...")
    
    # if user enters a question
    if question:
        # display user message
        with st.chat_message("user"):
            st.write(question)
        
        # add user message to chat history
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })
        
        # get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # get answer from AI
                    answer = ask_question(
                        question,
                        st.session_state.pdf_text,
                        language
                    )
                    
                    # display answer
                    st.write(answer)
                    
                    # add assistant message to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer
                    })
                except Exception as e:
                    # show error message
                    st.error(f"Error: {e}")
    
    # display MCQs if generated
    if st.session_state.mcqs:
        # divider line
        st.divider()
        
        # MCQs section header
        st.header("Practice Questions")
        
        # loop through each MCQ
        for i, mcq in enumerate(st.session_state.mcqs, 1):
            # create expandable section for each question
            with st.expander(f"Question {i}: {mcq['question'][:50]}..."):
                # display question
                st.write(f"**{mcq['question']}**")
                st.write("")
                
                # display all options
                for j, option in enumerate(mcq['options']):
                    st.write(f"{chr(65+j)}) {option}")
                
                # display correct answer
                st.write("")
                st.info(f"Correct Answer: {mcq['answer']}")

else:
    # landing page when no PDF is uploaded
    st.header("Welcome to BharatLearn AI")
    
    # create three columns
    col1, col2, col3 = st.columns(3)
    
    # column 1 - Upload feature
    with col1:
        st.markdown("""
        ### Upload PDF
        Upload your study material in PDF format
        """)
    
    # column 2 - Ask Questions feature
    with col2:
        st.markdown("""
        ### Ask Questions
        Get answers in 5 Indian languages
        """)
    
    # column 3 - Practice feature
    with col3:
        st.markdown("""
        ### Practice
        Generate MCQs and audio summaries
        """)
    
    # instruction message
    st.info("Upload a PDF file from the sidebar to get started")
