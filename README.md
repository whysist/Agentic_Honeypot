# Agentic Honeypot

An API-first AI honeypot for engaging potential scammers, selecting a victim persona, generating believable responses with LLMs, and extracting threat intelligence artifacts (IOCs) from the conversation.

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Run the FastAPI Backend](#run-the-fastapi-backend)
- [API Reference](#api-reference)
- [Demo Servers](#demo-servers)
- [Development Notes](#development-notes)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)

## Overview

This project simulates a scam victim conversation flow:

1. Receives incoming messages via `POST /honeypot`
2. Maintains per-session state in memory
3. Detects scam patterns with a risk-scoring detector
4. Assigns a persona based on detected categories
5. Generates short role-play replies (fallback + LLM providers)
6. Supports intelligence extraction utilities for IOC parsing
7. Exposes health and honeypot endpoints for integration

The codebase also includes Flask-based demo servers and a design spec (`DESIGN.md`) for a richer frontend/backend response model.

## How It Works

### 1) Session management

- `app/core/session_manager.py` stores sessions in an in-memory dictionary.
- Sessions are auto-cleaned with a TTL of 1 hour.
- Conversation history and counters are tracked per `sessionId`.

### 2) Scam detection

- `app/core/scam_detector.py` scores text with:
  - category regex hits (`bank_fraud`, `upi_fraud`, `phishing`, `urgency_tactics`, `fake_lottery`, `impersonation`)
  - link and phone-number signals
  - suspicious keyword boosts
  - multi-category synergy bonus
- Returns confidence and detected categories.

### 3) Persona selection

- `app/core/persona.py` maps scam categories to personas:
  - `confused_elderly`
  - `cautious_professional`
  - `naive_student`
  - `worried_parent`

### 4) Response generation

- `app/llm/chains/conversation_chain.py`
  - first two agent turns use naive fallback responses
  - then builds a persona-grounded prompt (`app/llm/prompts/honeypot_prompt.py`)
  - provider order: Gemini → HuggingFace → local fallback text

### 5) Intelligence extraction (utility)

- `app/core/intelligence.py` can extract:
  - bank accounts / IFSC-like patterns
  - UPI IDs
  - phishing links
  - phone numbers
  - suspicious keywords
- Callback service exists in `app/services/callback.py` for downstream reporting (currently not active in the main endpoint flow).

## Project Structure

```text
Agentic_Honeypot/
├── app/
│   ├── api/                  # FastAPI routes and dependency auth
│   │   ├── honeypot.py
│   │   ├── health.py
│   │   └── deps.py
│   ├── core/                 # Session, detection, persona, intelligence logic
│   ├── llm/
│   │   ├── chains/           # Conversation and router chains
│   │   ├── prompts/          # Prompt templates
│   │   ├── providers/        # Gemini / HuggingFace / Groq provider adapters
│   │   └── schemas/          # Pydantic schema models
│   ├── services/             # Callback integration
│   ├── storage/              # Pydantic models + Redis helper
│   ├── demo/                 # Flask demo servers + simple HTML UI
│   ├── config.py             # Environment-based runtime config
│   └── main.py               # FastAPI app entrypoint
├── DESIGN.md                 # Product/API/UI design plan
├── requirements.txt
└── README.md
```

## Tech Stack

- **Backend framework**: FastAPI
- **Data models**: Pydantic v2
- **LLM integrations**: Gemini, HuggingFace (and Groq utility chain support)
- **HTTP clients**: `requests`, provider SDKs
- **Demo servers**: Flask
- **Optional persistence helper**: Redis utility module

## Prerequisites

- Python 3.10+ recommended
- `pip` and virtual environment support
- API keys for selected providers (Gemini / HuggingFace / etc.)

## Installation

```bash
git clone https://github.com/whysist/Agentic_Honeypot.git
cd Agentic_Honeypot
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Create an environment file (or export env vars) for runtime configuration.

> The app loads environment variables via `dotenv` in `app/config.py`.

Recommended variables:

```bash
# API auth
API_KEY=change_me

# LLM providers
GEMINI_API_KEY=...
HUGGINGFACE_API_KEY=...
HF_MODEL=meta-llama/Llama-3.1-8B-Instruct
GROQ_API_KEY=...
CEREBRAS_API_KEY=...

# Callback and optional integrations
GUVI_CALLBACK_URL=https://your-callback-endpoint
REDIS_URL=redis://localhost:6379
```

## Run the FastAPI Backend

```bash
uvicorn app.main:app --reload --port 8000
```

Server starts with:

- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## API Reference

### `GET /health`

Returns service status and timestamp.

Example response:

```json
{
  "status": "healthy",
  "timestamp": "2026-04-20T15:00:00.000000"
}
```

### `POST /honeypot`

Protected by `x-api-key` header.

#### Request body

```json
{
  "sessionId": "session-123",
  "message": {
    "sender": "scammer",
    "text": "Your account is blocked. Verify immediately.",
    "timestamp": 1738972800000
  },
  "conversationHistory": [],
  "metadata": {}
}
```

#### Example cURL

```bash
curl -X POST "http://localhost:8000/honeypot" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{
    "sessionId": "demo-session-1",
    "message": {
      "sender": "scammer",
      "text": "Your account has been suspended. Click https://fake-bank.example and verify now.",
      "timestamp": 1738972800000
    }
  }'
```

#### Current response shape

```json
{
  "sessionId": "demo-session-1",
  "status": "success",
  "message": {
    "sender": "agent",
    "text": "Thank you for your message.",
    "timestamp": 1738972801000
  }
}
```

## Demo Servers

The `app/demo/` folder includes quick Flask demos for local experimentation:

- `server.py` (Ollama local model)
- `server_gemini.py` (Gemini API)
- `server_cerebras.py` (Cerebras API)
- `index.html` (minimal UI)

Run a demo server:

```bash
python app/demo/server.py
```

Then open `http://localhost:5000`.

## Development Notes

- Main service state is currently in-memory (`SessionManager`) with 1-hour TTL.
- Redis helper exists in `app/storage/redis.py` but is not wired into FastAPI route flow.
- Callback dispatch code in `app/api/honeypot.py` is currently commented out.
- `DESIGN.md` documents a planned enriched response contract and frontend thinking panel.

## Troubleshooting

- **401 Unauthorized**: verify `x-api-key` matches server `API_KEY`.
- **503 API key not configured**: ensure `API_KEY` is set in environment.
- **LLM fallback responses only**: check provider keys (`GEMINI_API_KEY`, `HUGGINGFACE_API_KEY`) and network access.
- **Import/config errors**: confirm all required env vars referenced by provider modules are defined.
- **Dependency issues**: recreate virtual environment and reinstall `requirements.txt`.

## Roadmap

Near-term items reflected by `DESIGN.md`:

- Enriched `/honeypot` response including confidence/persona/intelligence/provider metadata
- Frontend split-panel chat + “thinking” dashboard
- Callback trigger logic for actionable IOC reporting
- Stronger persistence and production hardening
