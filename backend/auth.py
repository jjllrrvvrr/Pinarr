"""
Module d'authentification pour Pinarr
Gestion des sessions, hashage des mots de passe
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import bcrypt
from pydantic import BaseModel

# Configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    if ENVIRONMENT == "production":
        raise ValueError("SECRET_KEY must be set in production environment")
    else:
        SECRET_KEY = "dev-secret-key-not-for-production"

ALGORITHM = "HS256"
SESSION_EXPIRE_HOURS = int(os.getenv("SESSION_EXPIRE_HOURS", "24"))

security = HTTPBearer(auto_error=False)


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


def hash_password(password: str) -> str:
    """
    Hash un mot de passe avec bcrypt
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie un mot de passe contre son hash bcrypt
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crée un token JWT
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=SESSION_EXPIRE_HOURS)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Décode un token JWT
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


async def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """
    Dépendance FastAPI pour récupérer l'utilisateur courant
    Utilise le cookie de session
    """
    token = request.cookies.get("session_token")

    if not token:
        credentials: HTTPAuthorizationCredentials = await security(request)
        if credentials:
            token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str = payload.get("sub")
    user_id: int = payload.get("user_id")

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"username": username, "user_id": user_id}


async def get_current_active_user(request: Request) -> Dict[str, Any]:
    """
    Vérifie que l'utilisateur est authentifié et actif
    """
    user = await get_current_user(request)
    # Ici on pourrait vérifier si l'utilisateur est actif
    return user


def set_auth_cookie(response, token: str):
    """
    Définit le cookie de session sécurisé
    """
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=ENVIRONMENT == "production",  # True en production (HTTPS)
        samesite="Lax",
        max_age=SESSION_EXPIRE_HOURS * 3600,
        path="/",
    )


def clear_auth_cookie(response):
    """
    Supprime le cookie de session
    """
    response.delete_cookie(key="session_token", path="/")
