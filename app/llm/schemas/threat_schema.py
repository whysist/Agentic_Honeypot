from pydantic import BaseModel, Field
from typing import Literal


class ThreatAnalysis(BaseModel):
    threat_level: Literal["low", "medium", "high"]
    category: Literal[
        "benign",
        "prompt_injection",
        "malware",
        "reconnaissance",
        "data_exfiltration",
        "unknown",
    ]
    explanation: str = Field(
        ...,
        max_length=300,
        description="Concise explanation without revealing system logic",
    )
