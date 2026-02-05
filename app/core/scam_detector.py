import re
from typing import List, Tuple


class ScamDetector:
    """
    Rule-based scam detection engine.
    Stateless and deterministic.
    """

    def __init__(self):
        self.scam_patterns = {
            "bank_fraud": [
                r"bank account.*block",
                r"account.*suspend",
                r"verify.*account",
                r"update.*kyc",
                r"unauthorized.*transaction",
                r"account.*deactivat",
            ],
            "upi_fraud": [
                r"upi.*id",
                r"paytm.*wallet",
                r"google.*pay",
                r"phonepe",
                r"refund.*pending",
                r"payment.*fail",
            ],
            "phishing": [
                r"click.*link",
                r"verify.*here",
                r"confirm.*identity",
                r"reset.*password",
                r"http[s]?://(?!.*\.gov|.*\.bank)",
                r"bit\.ly",
                r"tinyurl",
            ],
            "urgency_tactics": [
                r"immediately",
                r"urgent",
                r"within.*hours",
                r"expire.*today",
                r"last.*chance",
                r"act now",
                r"limited.*time",
            ],
            "fake_lottery": [
                r"won.*prize",
                r"lottery.*winner",
                r"congratulations.*selected",
                r"claim.*reward",
            ],
            "impersonation": [
                r"tax.*department",
                r"income.*tax",
                r"police.*station",
                r"cyber.*cell",
                r"rbi.*official",
                r"government.*officer",
            ],
        }

        self.suspicious_keywords = [
            "urgent",
            "verify",
            "confirm",
            "suspend",
            "block",
            "expire",
            "immediately",
            "click here",
            "password",
            "otp",
            "cvv",
            "pin",
            "card number",
            "bank details",
            "refund",
        ]

    def detect_scam(self, text: str) -> Tuple[bool, List[str], float]:
        """
        Analyze text and determine scam likelihood.

        Returns:
            (is_scam, detected_categories, confidence_score)
        """
        text_lower = text.lower()
        detected_categories: List[str] = []
        total_matches = 0

        # Pattern matching
        for category, patterns in self.scam_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    if category not in detected_categories:
                        detected_categories.append(category)
                    total_matches += 1

        # Base confidence
        confidence = min(total_matches * 0.15, 1.0)

        # Additional indicators
        has_link = bool(re.search(r"http[s]?://", text_lower))
        has_phone = bool(re.search(r"\+?[0-9]{10,13}", text_lower))
        keyword_hits = sum(1 for kw in self.suspicious_keywords if kw in text_lower)

        if has_link:
            confidence += 0.2

        if has_phone and any(
            c in detected_categories for c in ("bank_fraud", "upi_fraud")
        ):
            confidence += 0.15

        if keyword_hits >= 3:
            confidence += 0.1

        confidence = min(confidence, 1.0)

        is_scam = confidence >= 0.3 or len(detected_categories) >= 2

        return is_scam, detected_categories, confidence
