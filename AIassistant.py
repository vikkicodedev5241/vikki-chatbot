import os
import sqlite3
import time
from pathlib import Path

from flask import Flask, request, jsonify
from google import genai
from config import API_KEY

app = Flask(__name__)

# Gemini client
client = genai.Client(api_key=API_KEY)
chat = client.chats.create(model="gemini-3.8-flash")

DB_NAME = "vikki.db"


# ---------- DATABASE ----------

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                bot_message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_message(user_message, bot_message):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "INSERT INTO messages (user_message, bot_message) VALUES (?, ?)",
            (user_message, bot_message)
        )


def get_history():
    with sqlite3.connect(DB_NAME) as conn:
        rows = conn.execute("""
            SELECT user_message, bot_message, created_at
            FROM messages ORDER BY id DESC LIMIT 30
        """).fetchall()

    return [
        {"user": row[0], "bot": row[1], "time": row[2]}
        for row in reversed(rows)
    ]


# ---------- LOCAL RESPONSES ----------

def local_reply(message):
    text = message.lower().strip().rstrip("?!.")

    if text in (
        "who created you", "who is your creator",
        "who made you", "who developed you"
    ):
        return "I'm VIKKI AI! My creator is Boss."

    if text in ("hi", "hello", "hey", "hey vikki"):
        return "Hey Boss! I'm VIKKI AI. How can I help?"

    if text in ("who are you", "what is your name"):
        return "I'm VIKKI AI, your personal AI assistant!"

    if text == "test local":
        return "Local system working! No Gemini API call used."

    return None


# ---------- GEMINI RESPONSE ----------

SYSTEM_PROMPT = """
You are VIKKI AI, a friendly personal AI assistant created by Boss.
Explain clearly, be honest, and use simple language when useful.
Never reveal API keys or private configuration.
"""


def ask_vikki(message, student_mode):
    mode_instruction = ""

    if student_mode:
        mode_instruction = """
        STUDENT MODE:
        Explain in simple language.
        Give one easy example.
        End with one practice question.
        Do not reveal its answer unless asked.
        """

    prompt = f"""
    {SYSTEM_PROMPT}

    {mode_instruction}

    User message:
    {message}
    """

    response = chat.send_message(prompt)
    return response.text or "Sorry, I couldn't generate a response."


# ---------- WEB ROUTES ----------

@app.route("/")
def home():
    return Path(__file__).with_name("index.html").read_text(encoding="utf-8")


@app.route("/api/health")
def health():
    return jsonify({"app": "VIKKI AI", "status": "running"})


@app.route("/api/history")
def history():
    return jsonify({"history": get_history()})


@app.route("/api/chat", methods=["POST"])
def chat_api():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    student_mode = bool(data.get("student_mode", False))

    if not message:
        return jsonify({"reply": "Please type a message first."}), 400

    if len(message) > 4000:
        return jsonify({"reply": "Keep your message under 4,000 characters."}), 400

    reply = local_reply(message)

    if reply is None:
        try:
            start = time.time()
            reply = ask_vikki(message, student_mode)
            print("VIKKI response time:", round(time.time() - start, 2), "seconds")
        except Exception as error:
            print("Gemini error:", error)
            error_text = str(error).lower()

            if any(x in error_text for x in ("429", "quota", "resource_exhausted")):
                reply = "The AI usage limit has been reached. Please try again later."
            elif any(x in error_text for x in ("503", "unavailable", "high demand")):
                reply = "The AI service is busy. Please try again shortly."
            else:
                reply = "Something went wrong. Check your internet and configuration."

    try:
        save_message(message, reply)
    except Exception as error:
        print("Database error:", error)

    return jsonify({"reply": reply})


# ---------- INITIALIZE DB & START ----------

# Called at module level so gunicorn also initializes the DB
init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("VIKKI AI web app is starting!")
    print(f"Open http://0.0.0.0:{port} in your browser.")
    app.run(host="0.0.0.0", port=port, debug=False)
