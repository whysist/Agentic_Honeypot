import time
from typing import Dict, List, Optional
from app.storage.models import SessionState, Message
from threading import Lock
SESSION_TTL_SECONDS = 3600  


class SessionManager:
    """
    In-memory session manager.
    Can be swapped with Redis / DB without touching API code.
    """

    def __init__(self):
        self._sessions: Dict[str, SessionState] = {}
        self._lock = Lock()

    # ─────────────────────────────────────────────
    # Session lifecycle
    # ─────────────────────────────────────────────

    def get_or_create(self, session_id: str) -> SessionState:
        with self._lock:
            self._cleanup_expired()
            if session_id not in self._sessions:
                self._sessions[session_id] = SessionState(
                    sessionId=session_id,
                    scamDetected=False,
                    totalMessagesExchanged=0,
                    agentNotes=None,
                )
            return self._sessions[session_id]

    def get(self, session_id: str) -> SessionState | None:
        return self._sessions.get(session_id)

    # ─────────────────────────────────────────────
    # Message handling
    # ─────────────────────────────────────────────

    def add_message(self, session: SessionState, message: Message) -> None:
        """
        Appends the message to server-side history and updates the counter.
        """
        session.conversationHistory.append(message)
        session.totalMessagesExchanged += 1

    # ─────────────────────────────────────────────
    # Scam state
    # ─────────────────────────────────────────────

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
            notes = (
                f"Scam detected. "
                f"Categories: {', '.join(categories)}. "
                f"Confidence: {confidence:.2f}."
            )
            session.agentNotes = notes

    # ─────────────────────────────────────────────
    # Expiration
    # ─────────────────────────────────────────────

    def _cleanup_expired(self) -> None:
        """Remove sessions older than TTL. Called under lock."""
        now = time.time()
        expired = [
            sid for sid, s in self._sessions.items()
            if now - s.createdAt > SESSION_TTL_SECONDS
        ]
        for sid in expired:
            del self._sessions[sid]

    # ─────────────────────────────────────────────
    # Serialization helpers
    # ─────────────────────────────────────────────

    def to_dict(self, session: SessionState) -> dict:
        """
        Convert session to a plain dict for LLM chains.
        """
        return {
            "sessionId": session.sessionId,
            "scamDetected": session.scamDetected,
            "scamCategories": session.scamCategories,
            "persona": session.persona,
            "totalMessagesExchanged": session.totalMessagesExchanged,
            "agentNotes": session.agentNotes,
        }


# ─────────────────────────────────────────────
# Singleton instance (import-safe)
# ─────────────────────────────────────────────

session_manager = SessionManager()
