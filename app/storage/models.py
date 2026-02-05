from pydantic import BaseModel,Field
from typing import List, Optional, Literal,Union
from datetime import datetime

class Message(BaseModel):
    sender:Literal["scammer","user"]
    text:str
    timestamp: Union[int, datetime]

class HoneypotRequest(BaseModel):
    sessionId:str
    message:Message
    conversationHistory: List[Message] = Field(default_factory=list)
    metadata:Optional[dict]=None

class HoneypotResponse(BaseModel):
    sessionId: str
    status: Literal["success", "error"]
    message: Message


class ExtractedIntelligence(BaseModel):
    bankAccounts:List[str]=[]
    upiIds:List[str]=[]
    phishingLinks:List[str]=[]
    phoneNumbers:List[str]=[]
    suspiciousKeywords:List[str]=[]

class SessionState(BaseModel):
    sessionId:str
    scamDetected:bool=False
    totalMessagesExchanged:int=0
    extractedIntelligence: ExtractedIntelligence = Field(
        default_factory=ExtractedIntelligence
    )
    agentNotes: Optional[str] = None
    callbackSent: bool = False


    