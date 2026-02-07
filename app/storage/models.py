from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal, Union
from datetime import datetime
import time


class Message(BaseModel):
    sender: str
    text: str
    timestamp: Union[int, datetime, str]

    @field_validator("sender")
    @classmethod
    def normalize_sender(cls, v):
        v = v.lower()
        if v not in {"scammer", "user", "agent"}:
            raise ValueError("Invalid sender")
        return v


class HoneypotRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Message] = Field(default_factory=list)
    metadata: Optional[dict] = None


class HoneypotResponse(BaseModel):
    sessionId: str
    status: Literal["success", "error"]
    message: Message


class ExtractedIntelligence(BaseModel):
    bankAccounts: List[str] = Field(default_factory=list)
    upiIds: List[str] = Field(default_factory=list)
    phishingLinks: List[str] = Field(default_factory=list)
    phoneNumbers: List[str] = Field(default_factory=list)
    suspiciousKeywords: List[str] = Field(default_factory=list)


class SessionState(BaseModel):
    sessionId: str
    scamDetected: bool = False
    scamCategories: List[str] = Field(default_factory=list)
    persona: Optional[str] = None
    totalMessagesExchanged: int = 0
    conversationHistory: List[Message] = Field(default_factory=list)
    extractedIntelligence: ExtractedIntelligence = Field(
        default_factory=ExtractedIntelligence
    )
    agentNotes: Optional[str] = None
    callbackSent: bool = False
    createdAt: float = Field(default_factory=time.time)
