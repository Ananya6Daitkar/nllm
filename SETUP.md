# Setup Guide - BharatLearn AI

## Quick Setup (3 Steps)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**For advanced version with LangChain:**
```bash
pip install -r requirements_langchain.txt
```

### Step 2: Configure API Key

1. Get your free Google Gemini API key from: https://makersuite.google.com/app/apikey

2. Create a `.env` file in the project root:
```bash
cp .env.example .env
```

3. Add your API key to `.env`:
```
GOOGLE_API_KEY=your_actual_api_key_here
```

### Step 3: Run the Application

```bash
# Simple version (recommended)
streamlit run app_simple.py

# Advanced version with LangChain
streamlit run app_with_langchain.py
```

The application will open in your browser at `http://localhost:8501`

---

## Detailed Installation

### Prerequisites

- **Python 3.8 or higher**
  ```bash
  python --version
  ```

- **pip package manager**
  ```bash
  pip --version
  ```

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ananya6Daitkar/nllm.git
   cd nllm
   ```

2. **Create virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   
   # Activate on macOS/Linux
   source venv/bin/activate
   
   # Activate on Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

5. **Run the application**
   ```bash
   streamlit run app_simple.py
   ```

---

## Troubleshooting

### Python Version Issues

```bash
# Check Python version
python --version

# If Python 3.8+ not found, install from python.org
```

### pip Installation Issues

```bash
# Upgrade pip
pip install --upgrade pip

# If pip not found
python -m ensurepip --upgrade
```

### Dependency Installation Errors

```bash
# Clear pip cache
pip cache purge

# Reinstall with no cache
pip install -r requirements.txt --no-cache-dir
```

### API Key Not Working

```bash
# Verify .env file exists
ls -la .env

# Check .env content (should show GOOGLE_API_KEY=...)
cat .env

# Test API key
python -c "import google.generativeai as genai; import os; from dotenv import load_dotenv; load_dotenv(); genai.configure(api_key=os.getenv('GOOGLE_API_KEY')); print('API key works!')"
```

### Streamlit Not Found

```bash
# Install streamlit explicitly
pip install streamlit

# Or reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

### Port Already in Use

```bash
# Run on different port
streamlit run app_simple.py --server.port 8502
```

---

## Platform-Specific Instructions

### macOS

```bash
# Install Python via Homebrew
brew install python@3.11

# Install dependencies
pip3 install -r requirements.txt

# Run application
streamlit run app_simple.py
```

### Windows

```bash
# Install Python from python.org
# Then in Command Prompt:

pip install -r requirements.txt
streamlit run app_simple.py
```

### Linux (Ubuntu/Debian)

```bash
# Install Python
sudo apt update
sudo apt install python3 python3-pip

# Install dependencies
pip3 install -r requirements.txt

# Run application
streamlit run app_simple.py
```

---

## Verification

After installation, verify everything works:

1. **Check Python**
   ```bash
   python --version
   # Should show 3.8 or higher
   ```

2. **Check dependencies**
   ```bash
   pip list | grep -E "streamlit|google-generativeai|PyPDF2|gtts"
   ```

3. **Check API key**
   ```bash
   cat .env
   # Should show GOOGLE_API_KEY=your_key
   ```

4. **Run application**
   ```bash
   streamlit run app_simple.py
   # Should open browser at http://localhost:8501
   ```

---

## Next Steps

- Upload a PDF and test Q&A functionality
- Try generating MCQs
- Test audio summaries
- Switch between different languages
- Read [README.md](README.md) for more information
- Check [RESUME_GUIDE.md](RESUME_GUIDE.md) for career guidance

---

## Getting Help

If you encounter issues:

1. Check this troubleshooting guide
2. Verify all prerequisites are met
3. Check GitHub Issues: https://github.com/Ananya6Daitkar/nllm/issues
4. Create a new issue with error details

---

**Setup complete! Start learning in your language.** 🎓
