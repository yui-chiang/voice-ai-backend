import os
import uuid
import logging
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from services.ai_service import AIService

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class TransactionItem(BaseModel):
    amount: float = Field(..., gt=0, description="Expense amount")
    description: str = Field(..., description="Short description of the expense")
    category: str = Field(..., description="Expense category (food, drink, transport, …)")


class VoiceResponse(BaseModel):
    status: str
    text: str
    transactions: list[TransactionItem]


class HealthResponse(BaseModel):
    status: str
    version: str
    service: str


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Voice Expense AI service starting up")
    yield
    logger.info("Voice Expense AI service shutting down")


app = FastAPI(
    title="Voice Expense AI",
    description="Microservice that converts voice or text into structured expense transactions.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_service = AIService()

ALLOWED_EXTENSIONS = {".m4a", ".wav", ".mp3", ".ogg", ".webm", ".mp4"}


# ---------------------------------------------------------------------------
# Routes — v1
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health():
    return HealthResponse(status="ok", version="1.0.0", service="voice-expense-ai")


@app.post("/v1/voice", response_model=VoiceResponse, tags=["expense"])
async def process_voice(file: UploadFile = File(...)):
    """
    Upload an audio file and receive structured expense transactions.

    Supported formats: m4a, wav, mp3, ogg, webm, mp4
    """
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{ext}'. Allowed: {ALLOWED_EXTENSIONS}",
        )

    temp_path = f"/tmp/vea_{uuid.uuid4().hex}{ext}"
    try:
        logger.info("Processing voice upload: %s", file.filename)
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        text = await ai_service.speech_to_text(temp_path)
        logger.info("Transcript: %s", text)

        raw_items = await ai_service.parse_transactions(text)
        transactions = [TransactionItem(**item) for item in raw_items]
        logger.info("Parsed %d transaction(s)", len(transactions))

        return VoiceResponse(status="success", text=text, transactions=transactions)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error processing voice: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# Keep legacy route for backwards compatibility
@app.post("/voice", response_model=VoiceResponse, include_in_schema=False)
async def process_voice_legacy(file: UploadFile = File(...)):
    return await process_voice(file)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
