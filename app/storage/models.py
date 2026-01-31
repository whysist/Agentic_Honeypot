from pydantic import BaseModel,Field
from typing import List, Optional, Literal
from datetime import datetime

class Message(BaseModel):
    sender:Literal["scammer","user"]
    text:str
    timestamp:datetime

class HoneypotRequest(BaseModel):
    sessionId:str
    message:Message
    conversationHistory: List[Message]=Field(default_factory=True)
    metadata:Optional[dict]=None

class HoneypotResponse(BaseModel):
    status:Literal["success","error"]
    reply:str

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
    extractedIntelligence:ExtractedIntelligence=ExtractedIntelligence()
    agentNotes:str

    