"""Service pour la gestion des uploads."""

import os
import uuid
from pathlib import Path
from fastapi import UploadFile
from config import (
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE_BYTES,
    ALLOWED_MIME_TYPES,
    UPLOAD_DIR,
)
from exceptions import InvalidUploadException


# Signatures de fichiers pour validation
IMAGE_SIGNATURES = {
    b'\xff\xd8\xff': 'jpeg',  # JPEG
    b'\x89PNG\r\n\x1a\n': 'png',  # PNG
    b'RIFF': 'webp',  # WebP (simplifié)
}


def _get_file_extension(filename: str) -> str:
    """Récupère l'extension du fichier en minuscules."""
    if not filename:
        return ""
    return Path(filename).suffix.lower()


def _validate_file_type(file: UploadFile) -> None:
    """Valide que le fichier est une image autorisée."""
    # Vérifier l'extension
    ext = _get_file_extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise InvalidUploadException(
            f"Format non supporté. Formats acceptés: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Vérifier le type MIME déclaré
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise InvalidUploadException("Type de fichier non valide")


def _validate_file_size(content: bytes) -> None:
    """Vérifie que la taille du fichier ne dépasse pas la limite."""
    size = len(content)
    if size > MAX_FILE_SIZE_BYTES:
        size_mb = size / (1024 * 1024)
        max_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
        raise InvalidUploadException(
            f"Fichier trop volumineux ({size_mb:.1f}MB). Maximum: {max_mb:.0f}MB"
        )


def _validate_image_content(content: bytes) -> None:
    """Vérifie que le contenu est bien une image valide."""
    if len(content) < 12:
        raise InvalidUploadException("Fichier trop petit")
    
    # Vérifier les signatures
    is_valid = False
    for signature, img_type in IMAGE_SIGNATURES.items():
        if content.startswith(signature):
            is_valid = True
            break
    
    # Vérifier WebP spécifiquement (structure différente)
    if content[:4] == b'RIFF' and content[8:12] == b'WEBP':
        is_valid = True
    
    if not is_valid:
        raise InvalidUploadException("Le fichier ne contient pas d'image valide")


def upload_image(file: UploadFile) -> dict:
    """
    Upload une image avec validation complète.
    
    Args:
        file: Le fichier uploadé via FastAPI
        
    Returns:
        Dict avec filename et path
    """
    # Validation du fichier
    if not file.filename:
        raise InvalidUploadException("Aucun fichier fourni")
    
    _validate_file_type(file)
    
    # Lire le contenu
    content = file.file.read()
    
    _validate_file_size(content)
    _validate_image_content(content)
    
    # Générer un nom de fichier unique
    ext = _get_file_extension(file.filename)
    filename = f"{uuid.uuid4()}{ext}"
    filepath = UPLOAD_DIR / filename
    
    # Sauvegarder le fichier
    try:
        with open(filepath, "wb") as buffer:
            buffer.write(content)
    except IOError as e:
        raise InvalidUploadException(f"Erreur lors de la sauvegarde: {str(e)}")
    
    return {
        "filename": filename,
        "path": f"/uploads/{filename}"
    }


def delete_image(filename: str) -> bool:
    """
    Supprime une image uploadée.
    
    Args:
        filename: Le nom du fichier à supprimer
        
    Returns:
        True si supprimé, False sinon
    """
    filepath = UPLOAD_DIR / filename
    
    # Sécurité: vérifier que le chemin reste dans UPLOAD_DIR
    try:
        filepath.relative_to(UPLOAD_DIR)
    except ValueError:
        return False
    
    if filepath.exists():
        filepath.unlink()
        return True
    
    return False
