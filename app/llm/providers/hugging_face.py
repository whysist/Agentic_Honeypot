import logging
import requests

from app.config import HUGGINGFACE_API_KEY, HF_MODEL

logger = logging.getLogger(__name__)

HF_API_URL = f"https://router.huggingface.co/models/{HF_MODEL}"
DEFAULT_TIMEOUT = 8


def generate_text(
    prompt: str,
    *,
    temperature: float = 0.8,
    top_p: float = 0.9,
    max_new_tokens: int = 120,
) -> str:
    if not HUGGINGFACE_API_KEY:
        raise RuntimeError("HUGGINGFACE_API_KEY not configured")

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
            headers={
                "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=DEFAULT_TIMEOUT,
        )
    except requests.exceptions.Timeout:
        raise RuntimeError("HuggingFace timeout")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"HuggingFace request failed: {e}")

    if response.status_code != 200:
        logger.error("HuggingFace %s: %s", response.status_code, response.text)
        raise RuntimeError("HuggingFace returned non-200")

    try:
        result = response.json()
    except ValueError:
        raise RuntimeError("Invalid JSON from HuggingFace")

    if isinstance(result, list) and len(result) > 0:
        return result[0].get("generated_text", "").strip()
    if isinstance(result, dict):
        return result.get("generated_text", "").strip()

    raise RuntimeError(f"Unexpected HuggingFace response format: {result}")
