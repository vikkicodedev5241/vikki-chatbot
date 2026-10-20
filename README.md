# VIKKI AI Chatbot

A personal AI chatbot built with **Python (Flask)**, **Google Gemini API**, and **SQLite**.

---

## 📁 Project Structure

```
vikki chatbot/
│
├── AIassistant.py       # Main Flask application and Gemini API backend
├── config.py            # API key configuration
├── index.html           # Modern dark-theme web UI (HTML, CSS, JavaScript)
├── requirements.txt     # Python package requirements
├── run.bat              # Quick double-click starter script for Windows
├── vikki.db             # SQLite database storing chat history
└── README.md            # Project documentation
```

---

## 🚀 How to Run

### Method 1: Using the launcher
Double-click `run.bat` in this folder.

### Method 2: From command prompt or PowerShell
```powershell
python AIassistant.py
```

Then open your browser and go to:
**http://127.0.0.1:5000**

---

## ⚡ Features
- **Interactive Web Chat**: Responsive dark-mode UI with immediate feedback.
- **Gemini Powered**: Uses `gemini-3.6-flash` via Google GenAI SDK.
- **Local Fallback Responses**: Fast built-in responses for creator info and greetings without consuming API quota.
- **Student Mode**: Formats answers into simple explanations, examples, and practice questions.
- **Persistent Chat History**: Saves conversations into SQLite (`vikki.db`) and retrieves recent messages.
