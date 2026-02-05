import re
from typing import List

from app.storage.models import Message, ExtractedIntelligence


class IntelligenceExtractor:
    """
    Extract Indicators of Compromise (IOCs) from conversation history.
    Stateless, regex-based, cheap to run every turn.
    """

    @staticmethod
    def extract(conversation_history: List[Message]) -> ExtractedIntelligence:
        all_text = " ".join(msg.text for msg in conversation_history).lower()

        intelligence = ExtractedIntelligence()

        # Bank account numbers & IFSC codes
        bank_patterns = [
            r"\b\d{9,18}\b",              # account numbers
            r"\b[a-z]{4}0[a-z0-9]{6}\b",  # IFSC codes
        ]

        for pattern in bank_patterns:
            intelligence.bankAccounts.extend(re.findall(pattern, all_text))

        # UPI IDs
        upi_pattern = r"\b[\w\.-]+@[\w\.-]+\b"
        upi_matches = re.findall(upi_pattern, all_text)

        valid_upi_providers = (
            "paytm",
            "okaxis",
            "ybl",
            "axisbank",
            "oksbi",
            "sbi",
            "upi",
        )

        intelligence.upiIds.extend(
            u for u in upi_matches if any(p in u for p in valid_upi_providers)
        )

        # Phishing links
        link_pattern = (
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|"
            r"[!*\\(\\),]|(?:%[0-9a-fA-F]{2}))+"
        )
        intelligence.phishingLinks.extend(re.findall(link_pattern, all_text))

        # Phone numbers
        phone_pattern = r"\+?[0-9]{10,13}"
        intelligence.phoneNumbers.extend(re.findall(phone_pattern, all_text))

        # Suspicious keywords
        suspicious_keywords = [
            "urgent",
            "verify",
            "immediately",
            "block",
            "suspend",
            "otp",
            "cvv",
            "pin",
            "password",
            "account number",
        ]

        for kw in suspicious_keywords:
            if kw in all_text:
                intelligence.suspiciousKeywords.append(kw)

        # Deduplicate everything       
        intelligence.bankAccounts = list(set(intelligence.bankAccounts))
        intelligence.upiIds = list(set(intelligence.upiIds))
        intelligence.phishingLinks = list(set(intelligence.phishingLinks))
        intelligence.phoneNumbers = list(set(intelligence.phoneNumbers))
        intelligence.suspiciousKeywords = list(set(intelligence.suspiciousKeywords))

        return intelligence
