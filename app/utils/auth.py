import hmac
import os
from fastapi import Header,HTTPException,status

API_KEY=os.getenv("HONEYPOT_API_KEY")

def verify_api_key(x_api_key:str=Header(...)):
    if not API_KEY:
        raise RuntimeError("API Key not configured")
    if not hmac.compare_digest(x_api_key,API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return x_api_key