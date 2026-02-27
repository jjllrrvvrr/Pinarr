"""
Routes d'authentification pour Pinarr
"""

from fastapi import APIRouter, HTTPException, status, Request, Response, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional

from database import SessionLocal
from auth import (
    LoginRequest,
    LoginResponse,
    verify_password,
    create_access_token,
    set_auth_cookie,
    clear_auth_cookie,
    get_current_user,
    hash_password,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


def get_db():
    """Dependency pour obtenir une session DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_by_username(db: Session, username: str):
    """Récupère un utilisateur par son username"""
    result = db.execute(
        text(
            "SELECT id, username, password_hash, is_admin FROM users WHERE username = :username"
        ),
        {"username": username},
    ).fetchone()

    if result:
        return {
            "id": result[0],
            "username": result[1],
            "password_hash": result[2],
            "is_admin": result[3],
        }
    return None


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    response: Response,
    credentials: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Connexion utilisateur
    """
    # Récupérer l'utilisateur
    user = get_user_by_username(db, credentials.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Vérifier le mot de passe
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Créer le token
    access_token = create_access_token(
        data={"sub": user["username"], "user_id": user["id"]}
    )

    # Définir le cookie
    set_auth_cookie(response, access_token)

    return LoginResponse(access_token=access_token, username=user["username"])


@router.post("/logout")
async def logout(response: Response):
    """
    Déconnexion utilisateur
    """
    clear_auth_cookie(response)
    return {"message": "Déconnexion réussie"}


@router.get("/me")
async def get_me(request: Request, user: dict = Depends(get_current_user)):
    """
    Récupère les informations de l'utilisateur connecté
    """
    return {"username": user["username"], "user_id": user["user_id"]}


@router.get("/check")
async def check_auth(request: Request):
    """
    Vérifie si l'utilisateur est authentifié
    """
    try:
        user = await get_current_user(request)
        return {"authenticated": True, "username": user["username"]}
    except HTTPException:
        return {"authenticated": False}


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.post("/change-password")
async def change_password(
    request: Request,
    response: Response,
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """
    Change le mot de passe de l'utilisateur
    """
    old_password = data.old_password
    new_password = data.new_password

    # Vérifier l'ancien mot de passe
    db_user = get_user_by_username(db, user["username"])

    if not db_user or not verify_password(old_password, db_user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ancien mot de passe incorrect",
        )

    # Mettre à jour le mot de passe
    new_hash = hash_password(new_password)
    db.execute(
        text("UPDATE users SET password_hash = :hash WHERE id = :id"),
        {"hash": new_hash, "id": user["user_id"]},
    )
    db.commit()

    # Déconnecter toutes les sessions
    clear_auth_cookie(response)

    return {"message": "Mot de passe mis à jour avec succès"}


from pydantic import BaseModel


class UpdateProfileRequest(BaseModel):
    new_username: str


@router.post("/update-profile")
async def update_profile(
    request: Request,
    response: Response,
    data: UpdateProfileRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """
    Met à jour le profil utilisateur (nom d'utilisateur)
    """
    new_username = data.new_username

    if not new_username or new_username.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nom d'utilisateur ne peut pas être vide",
        )

    # Vérifier si le nouveau username existe déjà
    existing_user = get_user_by_username(db, new_username)
    if existing_user and existing_user["id"] != user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce nom d'utilisateur est déjà pris",
        )

    # Mettre à jour le username
    db.execute(
        text("UPDATE users SET username = :username WHERE id = :id"),
        {"username": new_username, "id": user["user_id"]},
    )
    db.commit()

    # Créer un nouveau token avec le nouveau username
    access_token = create_access_token(
        data={"sub": new_username, "user_id": user["user_id"]}
    )

    # Mettre à jour le cookie
    set_auth_cookie(response, access_token)

    return {"message": "Nom d'utilisateur mis à jour", "username": new_username}
