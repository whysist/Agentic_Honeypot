import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

API_KEY = os.getenv("HONEYPOT_API_KEY")
GUVI_CALLBACK_URL = os.getenv("GUVI_CALLBACK_URL", "https://guvi-hackathon.co/api/callback")

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_MODEL = os.getenv("HF_MODEL", "meta-llama/Llama-3.2-3B-Instruct")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

if not API_KEY:
    logger.warning("HONEYPOT_API_KEY not set — auth will reject all requests")

if not GEMINI_API_KEY and not HUGGINGFACE_API_KEY:
    logger.warning("No LLM API keys set — all replies will be fallback responses")
