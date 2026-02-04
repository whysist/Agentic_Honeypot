from typing import List, Dict, Any
from pydantic import BaseModel


class LLMMessage(BaseModel):
    role: str   # "scammer" | "user"
    content: str


class ConversationContext(BaseModel):
    """
    Internal structure passed into LLM chains.
    """
    messages: List[LLMMessage]
    persona: str
    scamCategories: List[str]


class LLMResponse(BaseModel):
    """
    Normalized LLM output (optional, future-proofing).
    """
    text: str
    raw: Dict[str, Any] | None = None
