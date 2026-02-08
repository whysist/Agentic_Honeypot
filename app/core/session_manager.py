import time
from typing import Dict, List, Optional
from app.storage.models import SessionState, Message
from threading import Lock

SESSION_TTL_SECONDS = 3600


class SessionManager:

    def __init__(self):
        self._sessions: Dict[str, SessionState] = {}
        self._lock = Lock()

    def get_or_create(self, session_id: str) -> SessionState:
        with self._lock:
            self._cleanup_expired()
            if session_id not in self._sessions:
                self._sessions[session_id] = SessionState(sessionId=session_id)
            return self._sessions[session_id]

    def get(self, session_id: str) -> SessionState | None:
        return self._sessions.get(session_id)

    def add_message(self, session: SessionState, message: Message) -> None:
        session.conversationHistory.append(message)
        session.totalMessagesExchanged += 1

    def set_scam(
        self,
        session: SessionState,
        detected: bool,
        categories: List[str],
        confidence: float,
        persona: Optional[str] = None,
    ) -> None:
        session.scamDetected = detected
        session.scamCategories = categories
        session.persona = persona
        if detected:
            session.agentNotes = (
                f"Scam detected. "
                f"Categories: {', '.join(categories)}. "
                f"Confidence: {confidence:.2f}."
            )

    def _cleanup_expired(self) -> None:
        now = time.time()
        expired = [
            sid for sid, s in self._sessions.items()
            if now - s.createdAt > SESSION_TTL_SECONDS
        ]
        for sid in expired:
            del self._sessions[sid]


session_manager = SessionManager()
