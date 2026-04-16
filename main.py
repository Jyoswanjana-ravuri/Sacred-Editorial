from fastapi import FastAPI, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from starlette.concurrency import run_in_threadpool

from DB.db import SessionLocal, Shloka
from services.managuru import managuru_service

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
app = FastAPI(
    title="Bhagavad Gita API",
    description="A simplified API for fetching Sanskrit slokas and receiving Gita-inspired guidance from Mana Guru.",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas
app.mount("/audio", StaticFiles(directory="DB/audio"), name="audio")
class GuidanceRequest(BaseModel):
    query: str

class GuidanceResponse(BaseModel):
    query: str
    guidance: str

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Bhagavad Gita API",
        "docs_url": "/docs",
        "endpoints": ["/sloka", "/managuru"]
    }

@app.get("/sloka")
def get_sloka(
    request: Request,
    chapter_id: int = Query(..., description="Chapter number (1-18)"),
    shloka_id: int = Query(..., description="Shloka/Verse number"),
    db: Session = Depends(get_db)
):
    """
    Retrieves a single sloka by its Chapter and Shloka ID.
    """
    db_sloka = db.query(Shloka).filter(
        Shloka.chapter == chapter_id,
        Shloka.verse == shloka_id
    ).first()

    if not db_sloka:
        raise HTTPException(
            status_code=404, 
            detail=f"Sloka not found for Chapter {chapter_id}, Shloka {shloka_id}"
        )

    return {
        "chapter_id": db_sloka.chapter,
        "shloka_id": db_sloka.verse,
        "shloka_sanskrit": db_sloka.sanskrit_text,
        "transliteration": db_sloka.transliteration,
        "english_meaning": db_sloka.english_meaning,
        "audio_url": str(request.base_url) + f"audio/{chapter_id}/{shloka_id}.wav"
    }

@app.post("/managuru", response_model=GuidanceResponse)
async def get_guidance(request: GuidanceRequest):
    """
    Provides empathetic, Gita-inspired guidance for your life questions.
    Uses the Suru/Bhagvad-Gita-LLM model.
    """
    try:
        # Run the heavy generation in a threadpool to avoid blocking FastAPI
        guidance = await run_in_threadpool(
            managuru_service.generate_guidance, 
            request.query
        )
        return {
            "query": request.query,
            "guidance": guidance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Guidance error: {str(e)}")
