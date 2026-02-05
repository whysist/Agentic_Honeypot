"""
Configuration for Agentic Honeypot API
"""
import os

# API Configuration
API_KEY = os.getenv("HONEYPOT_API_KEY")
GUVI_CALLBACK_URL = os.getenv("GUVI_CALLBACK_URL", "https://guvi-hackathon.co/api/callback")

# HuggingFace Configuration
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_MODEL = os.getenv("HF_MODEL", "meta-llama/Llama-3.2-3B-Instruct")

# Optional
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")