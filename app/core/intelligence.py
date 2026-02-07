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

        # IFSC codes (specific format: 4 letters + 0 + 6 alphanumeric)
        ifsc_pattern = r"\b[a-z]{4}0[a-z0-9]{6}\b"
        intelligence.bankAccounts.extend(re.findall(ifsc_pattern, all_text))

        # Bank account numbers: require a context word nearby
        # Matches 9-18 digit sequences preceded by account-related words
        account_pattern = r"(?:account|a/c|acct|acc)\s*(?:no\.?|number|num|#)?\s*:?\s*(\d{9,18})"
        intelligence.bankAccounts.extend(re.findall(account_pattern, all_text))

        # UPI IDs (email-like patterns filtered by known UPI providers)
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

        # Phone numbers: require word boundary, 10-13 digits with optional +
        phone_pattern = r"(?<!\d)\+?\d{10,13}(?!\d)"
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
