"""Dépendances FastAPI réutilisables."""

from fastapi import Depends, Request
from fastapi.responses import JSONResponse
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


async def pinarr_exception_handler(request: Request, exc: PinarrException):
    """Gestionnaire d'exceptions métier : renvoie une vraie réponse JSON.

    handle_pinarr_exception produit une HTTPException (non appelable en
    tant que réponse) : on extrait status_code/detail pour construire la
    JSONResponse attendue par FastAPI.
    """
    http_exc = handle_pinarr_exception(exc)
    return JSONResponse(status_code=http_exc.status_code, content={"detail": http_exc.detail})