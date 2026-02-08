import logging
import requests

from app.config import GUVI_CALLBACK_URL
from app.storage.models import SessionState, ExtractedIntelligence

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 10


def send_final_result(
    session: SessionState,
    intelligence: ExtractedIntelligence,
) -> bool:
    """
    Send extracted intelligence to external callback endpoint.
    Returns True on success, False on failure.
    Fires at most once per session (caller enforces this).
    """

    payload = {
        "sessionId": session.sessionId,
        "scamDetected": session.scamDetected,
        "totalMessagesExchanged": session.totalMessagesExchanged,
        "extractedIntelligence": intelligence.dict(),
        "agentNotes": session.agentNotes or "",
    }

    try:
        response = requests.post(
            GUVI_CALLBACK_URL,
            json=payload,
            timeout=TIMEOUT_SECONDS,
        )

        if response.status_code == 200:
            logger.info(
                "Callback sent successfully for session %s",
                session.sessionId,
            )
            return True
        else:
            logger.error(
                "Callback failed (%s): %s",
                response.status_code,
                response.text,
            )
            return False

    except requests.RequestException as e:
        logger.error("Callback request error: %s", e)
        return False
