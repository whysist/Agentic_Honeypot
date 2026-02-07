import requests
import logging
from typing import Optional

from app.config import (
    HUGGINGFACE_API_KEY,
    HF_MODEL,
)

logger = logging.getLogger(__name__)

HF_API_URL = f"https://router.huggingface.co/models/{HF_MODEL}"

DEFAULT_TIMEOUT = 8  # seconds


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json",
    }


def generate_text(
    prompt: str,
    *,
    temperature: float = 0.8,
    top_p: float = 0.9,
    max_new_tokens: int = 120,
) -> str:
    """
    Send prompt to Hugging Face Inference API and return generated text.

    Raises:
        RuntimeError on hard failures
    """

    payload = {
        "inputs": prompt,
        "parameters": {
            "temperature": temperature,
            "top_p": top_p,
            "max_new_tokens": max_new_tokens,
            "return_full_text": False,
        },
    }

    try:
        response = requests.post(
            HF_API_URL,
            headers=_headers(),
            json=payload,
            timeout=DEFAULT_TIMEOUT,
        )

    except requests.exceptions.Timeout:
        logger.error("HuggingFace request timed out")
        raise RuntimeError("LLM timeout")

    except requests.exceptions.RequestException as e:
        logger.error(f"HuggingFace request failed: {e}")
        raise RuntimeError("LLM request failed")

    if response.status_code != 200:
        logger.error(
            f"HuggingFace error {response.status_code}: {response.text}"
        )
        raise RuntimeError("LLM returned non-200 response")

    try:
        result = response.json()
    except ValueError:
        logger.error("Invalid JSON from HuggingFace")
        raise RuntimeError("Invalid LLM response")

    # HF usually returns a list of dicts
    if isinstance(result, list) and len(result) > 0:
        return result[0].get("generated_text", "").strip()

    # Fallback shape (rare but defensive)
    if isinstance(result, dict):
        return result.get("generated_text", "").strip()

    logger.error(f"Unexpected HuggingFace response format: {result}")
    raise RuntimeError("Unexpected LLM response format")
