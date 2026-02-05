from typing import Dict, List
from app.storage.models import SessionState, Message
from threading import Lock


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
            if session_id not in self._sessions:
                self._sessions[session_id] = SessionState(
                    sessionId=session_id,
                    scamDetected=False,
                    totalMessagesExchanged=0,
                    agentNotes=None
                )
            return self._sessions[session_id]

    def get(self, session_id: str) -> SessionState | None:
        return self._sessions.get(session_id)

    # ─────────────────────────────────────────────
    # Message handling
    # ─────────────────────────────────────────────

    def add_message(self, session: SessionState, message: Message) -> None:
        """
        Updates counters only.
        Message history itself is maintained upstream (LLM context).
        """
        session.totalMessagesExchanged += 1

    # ─────────────────────────────────────────────
    # Scam state
    # ─────────────────────────────────────────────

    def set_scam(
        self,
        session: SessionState,
        detected: bool,
        categories: List[str],
        confidence: float
    ) -> None:
        session.scamDetected = detected

        if detected:
            notes = (
                f"Scam detected. "
                f"Categories: {', '.join(categories)}. "
                f"Confidence: {confidence:.2f}."
            )
            session.agentNotes = notes

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
            "totalMessagesExchanged": session.totalMessagesExchanged,
            "agentNotes": session.agentNotes
        }


# ─────────────────────────────────────────────
# Singleton instance (import-safe)
# ─────────────────────────────────────────────

session_manager = SessionManager()
