from app.storage.redis import get_session, save_session
from app.core.detector import detect_scam
from app.core.agent import generate_agent_reply
from app.core.extractor import extract_intelligence
from app.storage.models import HoneypotRequest

async def process_message(payload:HoneypotRequest)->str:
    session = await get_session(payload.sessionId)

    session.messageCount += 1

    # Detect scam intent
    is_scam, confidence = detect_scam(payload.message.text)

    if is_scam:
        session.scamDetected = True
        session.confidence = max(session.confidence, confidence)
        
        extract_intelligence(
            payload.message.text,
            session.intelligence
        )

        reply = await generate_agent_reply(
            payload.message.text,
            session.messageCount
        )
    else:
        reply = "Sorry, I don’t understand this message."

    await save_session(session)
    return reply
