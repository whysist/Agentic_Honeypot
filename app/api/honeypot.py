from fastapi import APIRouter, Depends, HTTPException
from app.storage.models import HoneypotRequest, HoneypotResponse
from app.utils.auth import verify_api_key
from app.core.orchestrator import process_message

router = APIRouter()


@router.post("/api/honeypot", response_model=HoneypotResponse)
async def honeypot_endpoint(
    payload: HoneypotRequest,
    api_key: str = Depends(verify_api_key)
):
    try:
        reply = await process_message(payload)
        return HoneypotResponse(status="success", reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
