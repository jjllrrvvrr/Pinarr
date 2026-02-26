"""Dépendances FastAPI réutilisables."""

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from exceptions import SudoWineException, handle_sudowine_exception
from typing import Generator


def get_db() -> Generator[Session, None, None]:
    """Fournit une session de base de données."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def sudowine_exception_handler(request, exc: SudoWineException):
    """Gestionnaire d'exceptions personnalisé."""
    raise handle_sudowine_exception(exc)
