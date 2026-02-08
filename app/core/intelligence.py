import re
from typing import List

from app.storage.models import Message, ExtractedIntelligence


class IntelligenceExtractor:

    SUSPICIOUS_KEYWORDS = [
        "urgent", "verify", "immediately", "block", "suspend",
        "otp", "cvv", "pin", "password", "account number",
    ]

    VALID_UPI_PROVIDERS = (
        "paytm", "okaxis", "ybl", "axisbank", "oksbi", "sbi", "upi",
    )

    @classmethod
    def extract(cls, conversation_history: List[Message]) -> ExtractedIntelligence:
        all_text = " ".join(msg.text for msg in conversation_history).lower()
        intelligence = ExtractedIntelligence()

        # IFSC codes: 4 letters + 0 + 6 alphanumeric
        intelligence.bankAccounts.extend(
            re.findall(r"\b[a-z]{4}0[a-z0-9]{6}\b", all_text)
        )

        # Bank account numbers preceded by context words
        intelligence.bankAccounts.extend(
            re.findall(
                r"(?:account|a/c|acct|acc)\s*(?:no\.?|number|num|#)?\s*:?\s*(\d{9,18})",
                all_text,
            )
        )

        # UPI IDs filtered by known providers
        upi_matches = re.findall(r"\b[\w\.-]+@[\w\.-]+\b", all_text)
        intelligence.upiIds.extend(
            u for u in upi_matches
            if any(p in u for p in cls.VALID_UPI_PROVIDERS)
        )

        # Phishing links
        intelligence.phishingLinks.extend(
            re.findall(
                r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|"
                r"[!*\\(\\),]|(?:%[0-9a-fA-F]{2}))+",
                all_text,
            )
        )

        # Phone numbers: 10-13 digits with optional +, not part of a longer sequence
        intelligence.phoneNumbers.extend(
            re.findall(r"(?<!\d)\+?\d{10,13}(?!\d)", all_text)
        )

        for kw in cls.SUSPICIOUS_KEYWORDS:
            if kw in all_text:
                intelligence.suspiciousKeywords.append(kw)

        # Deduplicate
        intelligence.bankAccounts = list(set(intelligence.bankAccounts))
        intelligence.upiIds = list(set(intelligence.upiIds))
        intelligence.phishingLinks = list(set(intelligence.phishingLinks))
        intelligence.phoneNumbers = list(set(intelligence.phoneNumbers))
        intelligence.suspiciousKeywords = list(set(intelligence.suspiciousKeywords))

        return intelligence
