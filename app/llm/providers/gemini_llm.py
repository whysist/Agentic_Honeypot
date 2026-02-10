import logging
import google.generativeai as genai

from app.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def generate_text(
    prompt: str,
    *,
    temperature: float = 0.8,
    top_p: float = 0.9,
    max_output_tokens: int = 150,
) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not configured")

    try:
        model = genai.GenerativeModel(
            "gemini-2.0-flash",
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                top_p=top_p,
                max_output_tokens=max_output_tokens,
            ),
        )
        response = model.generate_content(prompt)

        if not response.candidates:
            raise RuntimeError("Gemini returned empty response")

        text = response.text.strip()
        if not text:
            raise RuntimeError("Gemini returned blank text")

        return text

    except RuntimeError:
        raise
    except Exception as e:
        logger.error("Gemini request failed: %s", e)
        raise RuntimeError(f"Gemini error: {e}")
