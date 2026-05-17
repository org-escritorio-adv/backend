from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.database import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def check_health():
    return {"status": "ok"}


@router.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception:
        raise HTTPException(
            status_code=500, detail="Database connection failed"
        ) from None
