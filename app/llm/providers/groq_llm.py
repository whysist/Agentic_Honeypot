import os
from langchain_groq import ChatGroq


def groq_llm():
    return ChatGroq(
        model="llama3-8b-8192",
        temperature=0.2,
        api_key=os.getenv("GROQ_API_KEY"),
    )
