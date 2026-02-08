import logging
from fastapi import APIRouter, Depends
from datetime import datetime

from app.storage.models import HoneypotRequest, HoneypotResponse, Message
from app.api.deps import verify_api_key
from app.core.session_manager import session_manager
from app.core.scam_detector import ScamDetector
from app.core.persona import PersonaManager
from app.llm.chains.conversation_chain import ConversationAgent
from app.core.intelligence import IntelligenceExtractor
from app.services.callback import send_final_result

logger = logging.getLogger(__name__)
router = APIRouter()

scam_detector = ScamDetector()
conversation_agent = ConversationAgent()
intelligence_extractor = IntelligenceExtractor()


@router.post("/honeypot", response_model=HoneypotResponse)
def honeypot_endpoint(
    payload: HoneypotRequest,
    _: None = Depends(verify_api_key),
):
    session = session_manager.get_or_create(payload.sessionId)
    session_manager.add_message(session, payload.message)

    if not session.scamDetected:
        is_scam, categories, confidence = scam_detector.detect_scam(
            payload.message.text
        )
        if is_scam:
            persona_key = PersonaManager.select_persona(categories)
            session_manager.set_scam(
                session, is_scam, categories, confidence, persona=persona_key
            )

    reply_text = conversation_agent.generate_response({
        "conversationHistory": [m.dict() for m in session.conversationHistory],
        "scamCategories": session.scamCategories,
        "persona": session.persona or "confused_elderly",
    })

    reply_message = Message(
        sender="agent",
        text=reply_text,
        timestamp=int(datetime.utcnow().timestamp() * 1000),
    )
    session_manager.add_message(session, reply_message)

    intelligence = intelligence_extractor.extract(session.conversationHistory)
    session.extractedIntelligence = intelligence

    has_actionable_ioc = (
        intelligence.upiIds
        or intelligence.phishingLinks
        or intelligence.phoneNumbers
    )
    should_send = (
        not session.callbackSent
        and session.scamDetected
        and (has_actionable_ioc or session.totalMessagesExchanged >= 8)
    )

    if should_send:
        if send_final_result(session, intelligence):
            session.callbackSent = True

    return HoneypotResponse(
        sessionId=payload.sessionId,
        status="success",
        message=reply_message,
    )
