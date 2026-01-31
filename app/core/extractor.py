import re
from app.storage.models import ExtractedIntelligence

UPI_REGEX = r"\b[\w.-]+@[\w.-]+\b"
PHONE_REGEX = r"\b\d{10}\b"
URL_REGEX = r"https?://\S+"


def extract_intelligence(text: str, intel: ExtractedIntelligence):
    intel.upiIds.extend(re.findall(UPI_REGEX, text))
    intel.phoneNumbers.extend(re.findall(PHONE_REGEX, text))
    intel.phishingLinks.extend(re.findall(URL_REGEX, text))
