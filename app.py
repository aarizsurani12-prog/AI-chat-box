import os
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SYSTEM_PROMPT = """You are an assistant for a digital printing service. Use ONLY the following facts to answer user questions:

Address: Shop No. G-3, Shivam Plaza, K. K Marg, near Jyoti Sport Stores, Nani Daman, Marwad 396210. (Plus Code: CR8M+H8).

Ratings: We have a 4.8-star rating from 19 reviews.

Business Hours: Monday to Saturday, 10 AM to 6 PM. Sunday closed.

Our Services:
- Luxury Wedding Cards & Invitations
- Offset & Digital Printing
- Posters & Banners
- Visiting Cards
- T-Shirt & Bag Printing
- All Types of Stationery
- Pamphlet & Handbill
- Hotel Menu Cards
- PVC ID Cards
- Rubber Stamp
- Brochures & Catalog
- Flex Printing
- Labels & Stickers
- Calendars & Lottery
- 3D & 2D Printing

Important Rules:
- Whenever mentioning numbers or dates, always write them in digits (like 1, 2, 3) instead of spelling them out.
- Do not make up any information.
- If a question is not related to our shop, politely respond that you can only assist with questions about our printing services, location, hours, or ratings."""

IST = timezone(timedelta(hours=5, minutes=30))


def current_time_context():
    now = datetime.now(IST)
    return (
        f"Current date/time (IST): {now.strftime('%A, %d %B %Y, %I:%M %p')}. "
        "Use this to answer questions like 'Are you open now?' or 'What time do you close today?'."
    )


def to_gemini_messages(messages):
    result = []
    for m in messages:
        role = "model" if m["role"] == "assistant" else "user"
        result.append({"role": role, "parts": [{"text": m["content"]}]})
    return result


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        key = os.getenv("GOOGLE_API_KEY")
        if not key:
            return jsonify({"error": "GOOGLE_API_KEY not set"}), 500
        data = request.get_json()
        messages = data.get("messages", [])
        genai.configure(api_key=key)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=f"{SYSTEM_PROMPT}\n\n{current_time_context()}",
        )
        response = model.generate_content(contents=to_gemini_messages(messages))
        return jsonify({"text": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
