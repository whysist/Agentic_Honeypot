# Agentic Honeypot -- Frontend and API Design Document

## Why this document exists

The backend pipeline is working. Scam detection, persona selection, LLM-based conversation, intelligence extraction, and callbacks are all functional and tested. But the current API response only returns the agent's reply text. All the interesting internal state (what scam was detected, what persona is active, what intelligence has been extracted) is computed and then thrown away before the response is sent.

We need two things. First, the API needs to return all that internal state alongside the reply so a frontend can display it. Second, we need to build a frontend that lets a user play the role of a scammer and watch the system's internal decision-making in real time. This is the demo that hackathon judges will interact with.

---

## What the user sees

A split-screen interface. The right side is a chat window where the user types scam messages and the honeypot AI responds. The left side is a "thinking panel" that reveals what the AI is actually doing behind the scenes -- scam detection status, confidence, persona choice, and extracted intelligence.

The thinking panel (40% width) shows: scam detection badge with confidence bar, category chips, active persona card with traits, extracted IOCs grouped by type (bank accounts, UPI IDs, phishing links, phone numbers, keywords), and the LLM provider badge. The chat panel (60% width) shows the conversation with scammer messages on the right and agent replies on the left, plus an input bar at the bottom. Both panels scroll independently.

The visual style is a modern dark UI. Think Discord or Slack, not a terminal. Dark backgrounds, rounded cards, clean fonts, color-coded elements.

---

## Part 1: Backend Changes

### The problem

The current POST /honeypot response:

```json
{
  "sessionId": "abc-123",
  "status": "success",
  "message": {
    "sender": "agent",
    "text": "Oh no, what should I do?",
    "timestamp": 1738972800000
  }
}
```

The scam detection result, confidence score, chosen persona, extracted phone numbers and UPI IDs -- none of it is in the response. It all exists in the session object in memory, but the endpoint does not include it.

### The solution

Enrich the response to include everything the frontend needs. No new endpoints. Just return more data from the same POST /honeypot call.

### Enriched response shape

```json
{
  "sessionId": "abc-123",
  "status": "success",
  "message": {
    "sender": "agent",
    "text": "Oh no, what should I do?",
    "timestamp": 1738972800000
  },
  "scamDetected": true,
  "scamCategories": ["bank_fraud", "urgency_tactics"],
  "confidence": 0.75,
  "persona": "confused_elderly",
  "personaDescription": "an elderly person who is not tech-savvy and easily confused",
  "personaTraits": [
    "Uses simple language",
    "Gets confused by technical terms",
    "Asks for clarification often",
    "Mentions family or grandchildren",
    "Sounds worried and slow to understand"
  ],
  "extractedIntelligence": {
    "bankAccounts": ["9876543210123"],
    "upiIds": ["scammer@paytm"],
    "phishingLinks": ["https://fake-bank.example.com/verify"],
    "phoneNumbers": ["+919876543210"],
    "suspiciousKeywords": ["urgent", "verify", "block"]
  },
  "totalMessagesExchanged": 6,
  "provider": "Gemini",
  "callbackSent": false
}
```

### Backend changes, file by file

**app/storage/models.py** -- Add a `confidence` field to `SessionState` so the detection confidence survives across turns. Add a new Pydantic model `EnrichedHoneypotResponse` with all the fields above. Existing `HoneypotResponse` stays untouched.

**app/core/session_manager.py** -- Inside `set_scam`, store `session.confidence = confidence`. Right now the method receives the value but only uses it to format a string in `agentNotes`.

**app/llm/chains/conversation_chain.py** -- Change `generate_response` to return a `(reply_text, provider_name)` tuple instead of a plain string. Provider is `"Gemini"`, `"HuggingFace"`, or `"fallback"`.

**app/api/honeypot.py** -- Switch to `EnrichedHoneypotResponse`. Unpack the provider tuple from `generate_response`. Resolve persona details via `PersonaManager.get_persona_prompt_data()`. Populate all enriched fields from session state.

No changes needed to `main.py`, `config.py`, `deps.py`, `health.py`, `scam_detector.py`, `persona.py`, `intelligence.py`, `callback.py`, or any LLM provider file.

---

## Part 2: Frontend

### Technology and structure

React with Vite. No UI library, no CSS framework, no state management library. Pure React with custom CSS. One page, no router. Dependencies are just `react`, `react-dom`, `vite`, and `@vitejs/plugin-react`.

The frontend lives in a `frontend/` directory. During development it runs on port 3000 with Vite proxying `/honeypot` and `/health` to `http://localhost:8000`. In production, `VITE_API_BASE_URL` points to the deployed backend.

### Components

**App** -- Top-level layout. Header bar with title and "New Session" button, then a flex container with ThinkingPanel (left) and ChatPanel (right). Uses the `useChat` hook to manage all state.

**useChat hook** -- Holds the message list, the latest "thinking" object (all enriched fields), and a loading flag. Generates a random session ID on mount. Exposes `send(text)` (appends scammer message, calls API, appends agent reply, updates thinking state) and `reset()` (new session ID, clear everything).

**ChatPanel** -- Message list with auto-scroll and an input bar. Enter to send, button disabled while loading, typing indicator while waiting for a response.

**MessageBubble** -- Single chat message. Scammer messages right-aligned with dark purple background. Agent messages left-aligned with dark blue background. Sender label and timestamp in muted text.

**ThinkingPanel** -- Composes all sub-components. Shows a placeholder before the first message, then renders each section in order.

**ScamBadge** -- Yellow "Analyzing..." when `scamDetected` is false, red "SCAM DETECTED" with pulse animation when true. Confidence bar below fills 0-100%, color from yellow (low) to red (high).

**CategoryChips** -- Horizontal row of colored tag chips. Colors: bank_fraud red, phishing purple, urgency_tactics yellow, fake_lottery green, upi_fraud orange, impersonation blue.

**PersonaCard** -- Card with blue left border. Persona name as title (snake_case formatted to Title Case), description in italics, traits as bullet list.

**IntelligenceList** -- Grouped by IOC type (bank accounts, UPI IDs, phishing links, phone numbers, keywords). Monospaced green font. Empty groups hidden. New items fade in.

**ProviderBadge** -- Small pill. Purple for Gemini, blue for HuggingFace, gray for fallback.

**API wrapper (honeypot.js)** -- Single `sendMessage(payload)` function. POST to `/honeypot` with `x-api-key` header.

**Config (config.js)** -- Reads `VITE_API_BASE_URL` and `VITE_API_KEY` from env. Defaults base URL to `http://localhost:8000`.

### Color palette

Dark theme with CSS variables: `#0f0f1a` app background, `#1a1a2e` panels, `#16213e` cards, `#0f3460` input fields, `#e0e0e0` primary text, `#8888aa` muted text. Accents: `#e94560` red (scam/alerts), `#00d97e` green (intelligence), `#4e9af1` blue (persona), `#f5a623` yellow (confidence), `#a855f7` purple (provider). Bubbles: `#2d1b3d` scammer, `#1b2d3d` agent. Border radius 12px.

---

## Part 3: Data flow

1. User types a scam message and hits Enter.
2. Hook adds `{sender: "scammer", text, timestamp}` to local list, sets loading true.
3. Typing indicator appears. Hook calls `POST /honeypot` with session ID and message.
4. Backend runs full pipeline: scam detection, persona selection, LLM generation, intelligence extraction, callback check.
5. Backend returns enriched response with agent reply and all internal state.
6. Hook adds agent reply to message list, updates thinking state with enriched fields.
7. React re-renders both panels.

---

## Part 4: Important behaviors and edge cases

**Before scam detection.** `scamDetected` is false, `confidence` is 0.0, `scamCategories` is empty. Thinking panel shows "Analyzing..." in yellow. Persona defaults to "confused_elderly". Agent still replies.

**After detection, values freeze.** The `if not session.scamDetected` guard skips detection after the first positive. Confidence and categories stay fixed for the rest of the conversation.

**Intelligence only grows.** The extractor runs over full conversation history every turn. IOCs appear but never disappear. Treat as append-only.

**Early turns use fallback.** First two replies are hardcoded naive responses (provider shows "fallback"). LLM (Gemini, HuggingFace backup) kicks in from turn 3.

**New Session.** Generates new session ID, clears messages and thinking panel. Old session stays in backend memory until 1-hour TTL.

**API errors.** Non-200 responses show an error in the chat area. Thinking panel keeps its last known state.

---

## Part 5: Implementation order

**Step 1: Enrich the backend response.** Modify models.py, session_manager.py, conversation_chain.py, honeypot.py. Test with curl to verify the new JSON shape.

**Step 2: Scaffold the frontend.** Create the Vite project, configure proxy, set up config and API wrapper, write the useChat hook, create bare App with two empty panels. Verify the API call works from the browser.

**Step 3: Build the chat panel.** MessageBubble, ChatPanel with input bar and auto-scroll. Wire to useChat.

**Step 4: Build the thinking panel.** ScamBadge, CategoryChips, PersonaCard, IntelligenceList, ProviderBadge. Compose in ThinkingPanel.

**Step 5: Polish.** Global dark theme, loading indicator, New Session button, fade-in animations, final testing.

---

## How to verify it works

1. Start the backend: `uvicorn app.main:app --reload --port 8000`
2. Start the frontend: `cd frontend && npm run dev`
3. Open `http://localhost:3000`.
4. Type: "Your bank account has been blocked. Verify immediately at http://fake-bank.com"
5. Chat panel shows agent reply. Thinking panel shows SCAM DETECTED badge, confidence bar, category chips, persona card, phishing link in intelligence.
6. Send 2-3 more messages with phone numbers and UPI IDs. Intelligence list grows. Provider switches from "fallback" to "Gemini" after turn 2.
7. Click "New Session" and verify everything resets.
