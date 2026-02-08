import logging
import random
import re
from typing import Dict, List

from app.core.persona import PersonaManager
from app.llm.prompts.honeypot_prompt import HONEYPOT_PROMPT
from app.llm.providers import gemini_llm, hugging_face

logger = logging.getLogger(__name__)

PROVIDERS = [
    ("Gemini", gemini_llm.generate_text),
    ("HuggingFace", hugging_face.generate_text),
]


class ConversationAgent:

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

    def generate_response(self, session_data: Dict) -> str:
        conversation_history = session_data.get("conversationHistory", [])
        scam_categories = session_data.get("scamCategories", [])
        persona_key = session_data.get("persona", "confused_elderly")

        agent_turns = sum(
            1 for msg in conversation_history if msg.get("sender") == "agent"
        )

        if agent_turns < 2:
            return self._early_naive_reply(scam_categories)

        prompt = self._build_prompt(conversation_history, scam_categories, persona_key)

        for provider_name, provider_fn in PROVIDERS:
            try:
                raw = provider_fn(prompt)
                cleaned = self._clean_response(raw)
                if cleaned and len(cleaned) > 8:
                    logger.info("Reply generated via %s", provider_name)
                    return cleaned
            except Exception as e:
                logger.warning("%s failed: %s", provider_name, e)

        return self._fallback_reply(scam_categories)

    def _build_prompt(
        self,
        conversation_history: List[Dict],
        scam_categories: List[str],
        persona_key: str,
    ) -> str:
        persona = PersonaManager.get_persona_prompt_data(persona_key)

        conversation = ""
        for msg in conversation_history[-6:]:
            role = "Scammer" if msg.get("sender") == "scammer" else "You"
            conversation += f"{role}: {msg['text']}\n"

        return HONEYPOT_PROMPT.format(
            persona_description=persona["description"],
            persona_traits="\n".join(f"- {t}" for t in persona["traits"]),
            scam_categories=", ".join(scam_categories) or "unknown",
            conversation=conversation.strip(),
        )

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
