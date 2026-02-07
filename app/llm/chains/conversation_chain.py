import logging
import random
import re
from typing import Dict, List

from app.core.persona import PersonaManager
from app.llm.prompts.honeypot_prompt import HONEYPOT_PROMPT
from app.llm.providers.hugging_face import generate_text

logger = logging.getLogger(__name__)


class ConversationAgent:
    """
    Handles multi-turn conversation logic with scammers.
    Responsible for:
    - early naive replies
    - prompt construction
    - LLM invocation
    - response cleaning
    - fallback logic
    """

    def __init__(self):
        self.fallback_responses = {
            "bank_fraud": [
                "Oh no, I didn't realize my account could be blocked.",
                "I'm not very good with banking apps, can you explain?",
            ],
            "upi_fraud": [
                "I don't really understand UPI very well.",
                "That sounds confusing, what do I need to do?",
            ],
            "phishing": [
                "I'm not sure about clicking links, is it safe?",
                "Why do I need to reset my password?",
            ],
            "fake_lottery": [
                "Really? I won something?",
                "That sounds exciting! What should I do next?",
            ],
            "general": [
                "I'm not sure I understand, can you explain again?",
                "This is a bit confusing for me.",
            ],
        }

        # Used only for agent turns 1–2
        self.early_naive_responses = {
            "bank_fraud": [
                "Oh… I didn't know that could happen.",
                "I see, I'm not very familiar with bank procedures.",
            ],
            "upi_fraud": [
                "I'm not very good with UPI things.",
                "Okay, that sounds a bit confusing.",
            ],
            "phishing": [
                "Oh, I wasn't expecting that.",
                "Let me try to understand this.",
            ],
            "fake_lottery": [
                "Oh wow, really?",
                "That's surprising, I didn't expect that.",
            ],
            "impersonation": [
                "That sounds serious… what should I do?",
                "Okay, I'm listening.",
            ],
            "general": [
                "Oh, okay.",
                "Hmm, I'm not really sure.",
            ],
        }

    # ─────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────

    def generate_response(self, session_data: Dict) -> str:
        """
        Main entry point used by the API layer.
        """

        conversation_history = session_data.get("conversationHistory", [])
        scam_categories = session_data.get("scamCategories", [])
        persona_key = session_data.get("persona", "confused_elderly")

        agent_turns = sum(
            1 for msg in conversation_history if msg.get("sender") == "agent"
        )

        # Early naive replies (turns 1–2)
        if agent_turns < 2:
            return self._early_naive_reply(scam_categories)

        # Build prompt
        prompt = self._build_prompt(
            conversation_history,
            scam_categories,
            persona_key,
        )

        # Call LLM provider
        try:
            raw_response = generate_text(prompt)
            cleaned = self._clean_response(raw_response)

            if cleaned and len(cleaned) > 8:
                return cleaned

        except Exception as e:
            logger.warning("LLM call failed, using fallback: %s", e)

        return self._fallback_reply(scam_categories)

    # ─────────────────────────────────────────────
    # Prompt construction
    # ─────────────────────────────────────────────

    def _build_prompt(
        self,
        conversation_history: List[Dict],
        scam_categories: List[str],
        persona_key: str,
    ) -> str:
        persona = PersonaManager.get_persona_prompt_data(persona_key)

        conversation = ""
        for msg in conversation_history[-6:]:
            sender = msg.get("sender", "scammer")
            role = "Scammer" if sender == "scammer" else "You"
            conversation += f"{role}: {msg['text']}\n"

        return HONEYPOT_PROMPT.format(
            persona_description=persona["description"],
            persona_traits="\n".join(f"- {t}" for t in persona["traits"]),
            scam_categories=", ".join(scam_categories) or "unknown",
            conversation=conversation.strip(),
        )

    # ─────────────────────────────────────────────
    # Response handling
    # ─────────────────────────────────────────────

    def _clean_response(self, text: str) -> str:
        text = re.sub(r"^(you:|response:|assistant:)", "", text, flags=re.I)
        text = text.strip().strip('"').strip("'")

        sentences = re.split(r"[.!?]+", text)
        if len(sentences) > 2:
            text = ". ".join(sentences[:2]) + "."

        text = re.sub(r"\(.*?\)|\[.*?\]", "", text)
        return text.strip()

    def _fallback_reply(self, scam_categories: List[str]) -> str:
        for category in scam_categories:
            if category in self.fallback_responses:
                return random.choice(self.fallback_responses[category])
        return random.choice(self.fallback_responses["general"])

    def _early_naive_reply(self, scam_categories: List[str]) -> str:
        for category in scam_categories:
            if category in self.early_naive_responses:
                return random.choice(self.early_naive_responses[category])
        return random.choice(self.early_naive_responses["general"])
