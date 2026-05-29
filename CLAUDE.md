# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

AI chatbox for a digital printing service, built with Python (Flask) + Anthropic SDK. The assistant answers only questions about shop address, hours, and ratings — no fabricated information.

## Getting Started

```bash
# 1. Copy and fill in your API key
cp .env.example .env

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the dev server
python app.py
# → http://localhost:5000
```

## Architecture

- **`app.py`** — Flask backend. Single `/chat` POST endpoint that streams responses via Server-Sent Events (SSE) using `stream_with_context`.
- **`templates/index.html`** — Self-contained chat UI. Maintains `conversationHistory` in memory (JS array); sends the full history on each request. Reads SSE chunks with the Fetch Streams API.
- **Anthropic SDK** — Streaming via `client.messages.stream()`. The system prompt uses `cache_control: {type: "ephemeral"}` so it is prompt-cached across turns (saves tokens on every request after the first).
- **Model:** `claude-opus-4-8`. Change in `app.py` if needed.
- **No persistence** — conversation history lives only in the browser tab; refreshing resets it.
