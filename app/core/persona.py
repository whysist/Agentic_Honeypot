from typing import List


class PersonaManager:

    PERSONAS = {
        "confused_elderly": {
            "description": "an elderly person who is not tech-savvy and easily confused",
            "traits": [
                "Uses simple language",
                "Gets confused by technical terms",
                "Asks for clarification often",
                "Mentions family or grandchildren",
                "Sounds worried and slow to understand",
            ],
        },
        "cautious_professional": {
            "description": "a working professional who is careful and moderately tech-savvy",
            "traits": [
                "Asks verification questions",
                "Mentions work or being busy",
                "Prefers official channels",
                "Questions unusual requests",
            ],
        },
        "naive_student": {
            "description": "a young student who is active online but inexperienced",
            "traits": [
                "Uses casual language",
                "Gets excited by offers or prizes",
                "Mentions college or exams",
                "Responds quickly without much skepticism",
            ],
        },
        "worried_parent": {
            "description": "a parent who is concerned about family finances",
            "traits": [
                "Expresses concern about money",
                "Mentions children or household responsibilities",
                "Sounds anxious and protective",
            ],
        },
    }

    @classmethod
    def select_persona(cls, scam_categories: List[str]) -> str:
        if "fake_lottery" in scam_categories:
            return "naive_student"
        if "impersonation" in scam_categories:
            return "worried_parent"
        if "bank_fraud" in scam_categories or "upi_fraud" in scam_categories:
            return "confused_elderly"
        return "cautious_professional"

    @classmethod
    def get_persona_prompt_data(cls, persona_key: str) -> dict:
        return cls.PERSONAS.get(persona_key, cls.PERSONAS["confused_elderly"])
