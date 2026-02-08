from fastapi import FastAPI
from app.api.honeypot import router as honeypot_router
from app.api.health import router as health_router

app = FastAPI(
    title="Agentic Honey-Pot API",
    description="Scam Detection & Intelligence Extraction API",
    version="1.0.0"
)

# Register API Routers
app.include_router(honeypot_router)
app.include_router(health_router)
