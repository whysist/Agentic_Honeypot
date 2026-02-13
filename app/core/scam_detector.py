import re
from typing import List, Tuple


class ScamDetector:
    """
    Clean risk-scoring detector.

    Returns:
        confidence (0.0 - 1.0)
        detected_categories (List[str])
    """

    def __init__(self):

        # --- Pattern Groups (Precompiled) ---

        raw_patterns = {
            "bank_fraud": [
                r"bank account.*block",
                r"account.*suspend",
                r"verify.*account",
                r"update.*kyc",
                r"unauthorized.*transaction",
                r"account.*deactivat",
            ],
            "upi_fraud": [
                r"\bupi id\b",
                r"paytm wallet",
                r"google pay",
                r"phonepe",
                r"refund pending",
                r"payment failed?",
            ],
            "phishing": [
                r"click.*link",
                r"verify.*here",
                r"confirm.*identity",
                r"reset.*password",
                r"\bbit\.ly\b",
                r"\btinyurl\b",
            ],
            "urgency_tactics": [
                r"\bimmediately\b",
                r"\burgent\b",
                r"within.*hours",
                r"expire.*today",
                r"last.*chance",
                r"\bact now\b",
            ],
            "fake_lottery": [
                r"won.*prize",
                r"lottery.*winner",
                r"congratulations.*selected",
                r"claim.*reward",
            ],
            "impersonation": [
                r"tax department",
                r"income tax",
                r"police station",
                r"cyber cell",
                r"rbi official",
                r"government officer",
            ],
        }

        # Precompile
        self.compiled_patterns = {
            category: [re.compile(p, re.IGNORECASE) for p in patterns]
            for category, patterns in raw_patterns.items()
        }

        # Suspicious keywords
        self.suspicious_keywords = [
            "otp", "cvv", "pin", "card number",
            "bank details", "password", "verify",
            "urgent", "refund"
        ]

        # Strong indicators (high weight)
        self.link_pattern = re.compile(r"\bhttps?://[^\s]+\b", re.IGNORECASE)
        self.phone_pattern = re.compile(r"\b\+?[0-9]{10,13}\b")

    # --------------------------------------------------

    def detect_scam(self, text: str) -> Tuple[float, List[str]]:

        text_lower = text.lower()

        detected_categories: List[str] = []
        score = 0.0

        # --- Category Pattern Matching ---

        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(text_lower):
                    if category not in detected_categories:
                        detected_categories.append(category)
                        score += 0.18  # category weight
                    break  # prevent overcounting same category

        # --- Strong Indicators ---

        has_link = bool(self.link_pattern.search(text_lower))
        has_phone = bool(self.phone_pattern.search(text_lower))

        if has_link:
            score += 0.25

        if has_phone:
            score += 0.20

        # --- Suspicious Keywords (light weight) ---

        keyword_hits = sum(
            1 for kw in self.suspicious_keywords if kw in text_lower
        )

        if keyword_hits >= 2:
            score += 0.10
        elif keyword_hits == 1:
            score += 0.05

        # --- Category synergy bonus ---

        if len(detected_categories) >= 2:
            score += 0.15

        # --- Cap score cleanly ---

        confidence = min(round(score, 3), 1.0)

        return confidence, detected_categories
