import os
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Resolve templates folder relative to this file
template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
app = Flask(__name__, template_folder=template_dir)

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


def current_time_context() -> str:
    now = datetime.now(IST)
    return (
        f"Current date/time (IST): {now.strftime('%A, %d %B %Y, %I:%M %p')}. "
        "Use this to answer questions like 'Are you open now?' or 'What time do you close today?'."
    )


def get_client():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY environment variable is not set")
    return Groq(api_key=key)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    key = os.getenv("GROQ_API_KEY")
    return jsonify({"status": "ok", "key_set": bool(key)})


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        messages = data.get("messages", [])
        client = get_client()
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{current_time_context()}"}
            ] + messages,
        )
        reply = completion.choices[0].message.content
        return jsonify({"text": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
