"""Dépendances FastAPI réutilisables."""

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from exceptions import PinarrException, handle_pinarr_exception
from typing import Generator


def get_db() -> Generator[Session, None, None]:
    """Fournit une session de base de données."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def pinarr_exception_handler(request, exc: PinarrException):
    """Gestionnaire d'exceptions personnalisé."""
    raise handle_pinarr_exception(exc)
