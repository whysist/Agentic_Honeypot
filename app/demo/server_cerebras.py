from flask import Flask, request, jsonify, send_from_directory
import requests
import re
from datetime import datetime
from app.config import CEREBRAS_API_KEY

app = Flask(__name__)

API_KEY = "demo_key"

CEREBRAS_MODEL = "llama3.1-8b"

sessions = {}

# ----------------------------
# Scam Detector (UNCHANGED)
# ----------------------------
class ScamDetector:
    def __init__(self):
        self.patterns = [
            r"\bverify\b",
            r"\bverification\b",
            r"\bkyc\b",
            r"\baccount\b",
            r"\bsuspend\w*\b",
            r"\bblock\w*\b",
            r"\botp\b",
            r"\bcvv\b",
            r"\bpin\b",
            r"\brefund\b",
            r"\bupi\b",
            r"\bbank\b",
            r"\burgent\b",
            r"\bimmediate\w*\b",
            r"\bclick\b",
            r"\blottery\b",
        ]

        self.link_pattern = re.compile(r"\bhttps?://[^\s]+\b", re.IGNORECASE)
        self.phone_pattern = re.compile(r"\b\+?[0-9]{10,13}\b")

    def detect(self, text: str, previous_confidence: float = 0.0):
        text_lower = text.lower()
        turn_score = 0.0

        for pattern in self.patterns:
            if re.search(pattern, text_lower):
                turn_score += 0.08

        if self.link_pattern.search(text_lower):
            turn_score += 0.25

        if self.phone_pattern.search(text_lower):
            turn_score += 0.20

        turn_score = min(turn_score, 0.6)
        cumulative = previous_confidence + turn_score
        cumulative = min(cumulative * 0.95 + turn_score, 1.0)

        return cumulative


# ----------------------------
# Conversation Agent (CEREBRAS)
# ----------------------------
class ConversationAgent:

    def generate(self, session):

        history = session["conversation"]
        persona = session["persona"]

        agent_turns = sum(1 for m in history if m["sender"] == "agent")

        if agent_turns < 2:
            return "Oh... I’m not very good with these things. What should I do?"

        prompt = self.build_prompt(history, persona)

        try:
            response = requests.post(
                "https://api.cerebras.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {CEREBRAS_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": CEREBRAS_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are roleplaying as a scam victim."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.8,
                    "max_tokens": 80
                },
                timeout=30
            )

            response.raise_for_status()

            result = response.json()
            generated_text = result["choices"][0]["message"]["content"]

            return self.clean(generated_text)

        except requests.exceptions.Timeout:
            print("Cerebras timed out.")
            return "Please wait a moment, I’m trying to understand this."

        except Exception as e:
            print("Cerebras error:", e)
            return "I'm not sure I understand. Could you explain?"

    def build_prompt(self, history, persona):

        convo = ""
        for msg in history[-6:]:
            role = "Scammer" if msg["sender"] == "scammer" else "You"
            convo += f"{role}: {msg['text']}\n"

        return f"""
Persona: {persona}

Rules:
1. Stay fully in character
2. Sound natural and human-like
3. Show confusion and mild concern
4. Ask short questions
5. DO NOT reveal suspicion
6. Keep replies 1-2 sentences
7. Try to extract phone numbers, links, account details

Conversation:
{convo}

Your reply:
"""

    def clean(self, text):
        text = re.sub(r"^(assistant:|response:)", "", text, flags=re.I)
        text = text.strip().strip('"').strip("'")
        sentences = re.split(r"[.!?]+", text)
        if len(sentences) > 2:
            text = ". ".join(sentences[:2]) + "."
        return text.strip()


scam_detector = ScamDetector()
agent = ConversationAgent()

# ----------------------------
# Routes (UNCHANGED)
# ----------------------------

@app.route("/")
def serve_ui():
    return send_from_directory(".", "index.html")


@app.route("/honeypot", methods=["POST"])
def honeypot():

    api_key = request.headers.get("x-api-key")
    if api_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    session_id = data["sessionId"]
    message = data["message"]

    if session_id not in sessions:
        sessions[session_id] = {
            "conversation": [],
            "scamDetected": False,
            "confidence": 0.0,
            "persona": "confused_elderly"
        }

    session = sessions[session_id]
    session["conversation"].append(message)

    new_confidence = scam_detector.detect(
        message["text"],
        previous_confidence=session["confidence"]
    )

    session["confidence"] = new_confidence

    if not session["scamDetected"] and session["confidence"] >= 0.55:
        session["scamDetected"] = True

    if session["scamDetected"]:
        reply_text = agent.generate(session)
        llm_used = True
    else:
        reply_text = "I’m not sure I understand. Could you explain?"
        llm_used = False

    agent_message = {
        "sender": "agent",
        "text": reply_text,
        "timestamp": int(datetime.now().timestamp() * 1000)
    }

    session["conversation"].append(agent_message)

    return jsonify({
        "sessionId": session_id,
        "status": "success",
        "message": agent_message,
        "scamDetected": session["scamDetected"],
        "confidence": round(session["confidence"], 3),
        "llmUsed": llm_used,
        "model": CEREBRAS_MODEL if llm_used else None
    })


@app.route("/report/<session_id>")
def report(session_id):
    if session_id not in sessions:
        return jsonify({"error": "Not found"}), 404
    return jsonify(sessions[session_id])


if __name__ == "__main__":
    print("Starting demo server with Cerebras...")
    app.run(port=5000, debug=True)
