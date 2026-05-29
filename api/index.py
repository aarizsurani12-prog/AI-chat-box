import json
import os
from datetime import datetime, timezone, timedelta
from http.server import BaseHTTPRequestHandler
import google.generativeai as genai

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


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            key = os.getenv("GOOGLE_API_KEY")
            if not key:
                self._respond(500, {"error": "GOOGLE_API_KEY not set"})
                return

            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            messages = body.get("messages", [])

            genai.configure(api_key=key)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=f"{SYSTEM_PROMPT}\n\n{current_time_context()}",
            )
            response = model.generate_content(contents=to_gemini_messages(messages))
            self._respond(200, {"text": response.text})
        except Exception as e:
            self._respond(500, {"error": str(e)})

    def do_GET(self):
        key = os.getenv("GOOGLE_API_KEY")
        self._respond(200, {"status": "ok", "key_set": bool(key)})

    def _respond(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass
