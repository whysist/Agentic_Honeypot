from langchain_core.output_parsers import StrOutputParser
from app.llm.providers.gemini_llm import get_gemini
from prompts.base_prompt import BASE_PROMPT


def build_basic_chain():
    llm = get_gemini()
    parser = StrOutputParser()

    chain = BASE_PROMPT | llm | parser
    return chain
