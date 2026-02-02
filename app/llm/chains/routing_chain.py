from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException

from llm.schemas.threat_schema import ThreatAnalysis
from llm.prompts.base_prompt import BASE_PROMPT
from llm.gemini_llm import gemini_flash
from llm.groq_llm import groq_llm


class LLMRouter:
    def __init__(self):
        self.parser = PydanticOutputParser(pydantic_object=ThreatAnalysis)

        self.gemini_chain = BASE_PROMPT | gemini_flash() | self.parser
        self.groq_chain = BASE_PROMPT | groq_llm() | self.parser

    def analyze(self, user_input: str) -> ThreatAnalysis:
        try:
            return self.gemini_chain.invoke({"input": user_input})
        except OutputParserException:
            # Invalid JSON → fallback
            return self.groq_chain.invoke({"input": user_input})
        except Exception:
            # Timeout / provider failure
            return self.groq_chain.invoke({"input": user_input})
