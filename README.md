# BharatLearn AI

**Multilingual Educational Chatbot for Indian Languages**

An AI-powered learning platform that makes education accessible in 5 Indian languages. Upload PDFs, ask questions, generate practice MCQs, and listen to audio summaries.

---

## Features

- **Multilingual Q&A** - Ask questions in English, Hindi, Tamil, Telugu, or Marathi
- **PDF Processing** - Upload any educational document and extract text
- **MCQ Generation** - Automatically create 10 practice questions
- **Audio Summaries** - Listen to document summaries in your language
- **Clean UI** - Professional, distraction-free interface

---

## Quick Start

### Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your Google Gemini API key to .env file
GOOGLE_API_KEY=your_key_here

# 3. Run the application
streamlit run app_simple.py
```

Get your free API key: https://makersuite.google.com/app/apikey

### Usage

1. Open `http://localhost:8501` in your browser
2. Upload a PDF from the sidebar
3. Click "Process PDF"
4. Select your preferred language
5. Start asking questions!

---

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                     BharatLearn AI Workflow                  │
└─────────────────────────────────────────────────────────────┘

    📄 Upload PDF
         │
         ▼
    ┌─────────────┐
    │   PyPDF2    │  Extract text from PDF
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │   Storage   │  Store in session state
    └──────┬──────┘
           │
           ├──────────────┬──────────────┬──────────────┐
           │              │              │              │
           ▼              ▼              ▼              ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
    │   Q&A    │   │   MCQ    │   │  Audio   │   │ Language │
    │          │   │ Generate │   │ Summary  │   │  Select  │
    └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
         │              │              │              │
         └──────────────┴──────────────┴──────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │  Google Gemini   │  AI Processing
              │      API         │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  Response in     │  English, Hindi,
              │  Your Language   │  Tamil, Telugu,
              └──────────────────┘  or Marathi
```

---

## Technology Stack

- **Python** - Core programming language
- **Streamlit** - Web interface
- **Google Gemini API** - AI language model
- **PyPDF2** - PDF text extraction
- **gTTS** - Text-to-speech conversion

---

## Project Structure

```
bharatlearn-ai/
├── app_simple.py              # Main application (recommended)
├── app.py                     # Original version
├── app_with_langchain.py      # Advanced version with LangChain
├── requirements.txt           # Dependencies
├── requirements_langchain.txt # LangChain dependencies
├── .env                       # API keys (create this)
├── .env.example               # Environment template
├── README.md                  # This file
├── SETUP.md                   # Setup guide
├── INTERVIEW_GUIDE.md         # Interview preparation
└── RESUME_GUIDE.md            # Resume guidance
```

---

## Which Version to Use?

| Version | Best For | Features |
|---------|----------|----------|
| **app_simple.py** ⭐ | Learning, Interviews | Clean code, 5 dependencies |
| **app.py** | Understanding basics | Original implementation |
| **app_with_langchain.py** | Production | Semantic search, FAISS, source citations |

**Recommendation:** Start with `app_simple.py`

---

## Supported Languages

- English
- Hindi (हिंदी)
- Tamil (தமிழ்)
- Telugu (తెలుగు)
- Marathi (मराठी)

---

## Documentation

- **[SETUP.md](SETUP.md)** - Detailed installation guide
- **[INTERVIEW_GUIDE.md](INTERVIEW_GUIDE.md)** - Interview preparation
- **[RESUME_GUIDE.md](RESUME_GUIDE.md)** - How to add this to your resume

---

## Troubleshooting

**Audio not playing?**
- Use Chrome browser
- Check volume settings
- Audio player is in the sidebar

**API errors?**
```bash
# Check your .env file
cat .env

# Verify API key works
python -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); print('Success!')"
```

**Installation issues?**
```bash
# Upgrade pip
pip install --upgrade pip

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## License

MIT License - Free to use and modify


**Made for Indian learners** 🇮🇳
