SCAM_KEYWORDS = [
    "blocked", "suspended", "verify",
    "urgent", "upi", "bank", "immediately"
]


def detect_scam(text: str) -> tuple[bool, float]:
    hits = sum(1 for kw in SCAM_KEYWORDS if kw in text.lower())
    confidence = min(hits / len(SCAM_KEYWORDS), 1.0)
    return hits >= 2, confidence
