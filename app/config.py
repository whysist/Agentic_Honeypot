import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GUVI_CALLBACK_URL = os.getenv("GUVI_CALLBACK_URL")

OLLAMA_KEY=os.getenv("OLLAMA_KEY")