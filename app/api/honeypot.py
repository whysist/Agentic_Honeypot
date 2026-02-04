from fastapi import APIRouter, Depends
from datetime import datetime

from app.storage.models import HoneypotRequest,HoneypotResponse,Message

from app.api.deps import verify_api_key
from app.core.session_manager import session_manager
from app.core.scam_detector import ScamDetector
from app.llm.chains.conversation_chain import ConversationAgent

router = APIRouter()

scam_detector = ScamDetector()
conversation_agent = ConversationAgent()
from app.core.intelligence import IntelligenceExtractor
from app.services.callback import send_final_result

intelligence_extractor = IntelligenceExtractor()

@router.post("/honeypot", response_model=HoneypotResponse)
def honeypot_endpoint(
    payload: HoneypotRequest,
    _: None = Depends(verify_api_key)
):
    session = session_manager.get_or_create(payload.sessionId)

    # ── Add incoming message
    session_manager.add_message(session, payload.message)

    # ── Scam detection (first message only)
    if session.totalMessagesExchanged == 1:
        is_scam, categories, confidence = scam_detector.detect_scam(
            payload.message.text
        )
        session_manager.set_scam(session, is_scam, categories, confidence)

    # ── Generate agent reply
    reply_text = conversation_agent.generate_response({
        "conversationHistory": [m.dict() for m in payload.conversationHistory],
        "scamCategories": categories if session.scamDetected else [],
        "persona": session.agentNotes,
    })

    reply_message = Message(
        sender="user",
        text=reply_text,
        timestamp=int(datetime.utcnow().timestamp() * 1000),
    )

    session_manager.add_message(session, reply_message)

    # ── Intelligence extraction (every turn)
    intelligence = intelligence_extractor.extract(
        payload.conversationHistory + [reply_message]
    )
    session.extractedIntelligence = intelligence

    # ── Callback trigger conditions
    has_actionable_ioc = (
        intelligence.upiIds
        or intelligence.phishingLinks
        or intelligence.phoneNumbers
    )

    should_send = (
        not session.callbackSent
        and session.scamDetected
        and (
            has_actionable_ioc
            or session.totalMessagesExchanged >= 8
        )
    )

    if should_send:
        send_final_result(session, intelligence)
        session.callbackSent = True

    return HoneypotResponse(
        sessionId=payload.sessionId,
        status="success",
        message=reply_message,
    )
