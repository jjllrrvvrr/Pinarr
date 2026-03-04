"""Service pour la gestion des uploads."""

import os
import uuid
from pathlib import Path
from io import BytesIO
from PIL import Image
from fastapi import UploadFile
import requests
from config import (
    ALLOWED_EXTENSIONS,
    ALLOWED_MIME_TYPES,
    UPLOAD_DIR,
    MAX_FILE_SIZE_BYTES,
    MAX_FILE_SIZE_MB,
)
from exceptions import InvalidUploadException


# Signatures de fichiers pour validation
IMAGE_SIGNATURES = {
    b"\xff\xd8\xff": "jpeg",  # JPEG
    b"\x89PNG\r\n\x1a\n": "png",  # PNG
    b"RIFF": "webp",  # WebP (simplifié)
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

    # Vérifier le type MIME déclaré (moins strict pour les photos mobiles)
    if file.content_type:
        # Types MIME acceptés (incluant les variantes mobiles)
        accepted_types = ALLOWED_MIME_TYPES | {
            "image/heic-sequence",
            "image/heif-sequence",
        }
        if file.content_type not in accepted_types:
            # Si c'est une image quelconque, on accepte quand même
            if not file.content_type.startswith("image/"):
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
    if content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        is_valid = True

    # HEIC/HEIF signatures
    if content[4:8] in [b"ftyp", b"heic", b"heif"]:
        is_valid = True

    if not is_valid:
        raise InvalidUploadException("Le fichier ne contient pas d'image valide")


def _convert_and_compress_image(content: bytes, ext: str) -> tuple[bytes, str]:
    """
    Convertit HEIC/HEIF en JPG et compresse si nécessaire.
    Retourne (contenu, extension_finale).
    """
    try:
        # Essayer d'ouvrir avec PIL
        img = Image.open(BytesIO(content))

        # Convertir en RGB si nécessaire (pour HEIC/HEIF)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Si c'était un HEIC/HEIF, convertir en JPG
        if ext in [".heic", ".heif"]:
            output = BytesIO()
            img.save(output, format="JPEG", quality=85, optimize=True)
            return output.getvalue(), ".jpg"

        # Pour les autres formats, compresser si nécessaire
        # Redimensionner si trop grand (max 1920px)
        max_size = 1920
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        # Sauvegarder avec compression
        output = BytesIO()
        if ext == ".png":
            img.save(output, format="PNG", optimize=True)
        else:
            # JPG ou autre, convertir en JPG avec compression
            img.save(output, format="JPEG", quality=85, optimize=True)
            return output.getvalue(), ".jpg"

        return output.getvalue(), ext

    except Exception as e:
        # Si PIL ne peut pas ouvrir, retourner le contenu original
        return content, ext


def upload_image(file: UploadFile) -> dict:
    """
    Upload une image avec validation complète et conversion HEIC/HEIF.

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

    # Convertir et compresser si nécessaire
    content, final_ext = _convert_and_compress_image(content, ext)

    filename = f"{uuid.uuid4()}{final_ext}"
    filepath = UPLOAD_DIR / filename

    # Sauvegarder le fichier
    try:
        with open(filepath, "wb") as buffer:
            buffer.write(content)
    except IOError as e:
        raise InvalidUploadException(f"Erreur lors de la sauvegarde: {str(e)}")

    return {"filename": filename, "path": f"/uploads/{filename}"}


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


def upload_image_from_url(url: str) -> dict:
    """
    Télécharge une image depuis une URL et la sauvegarde localement.

    Args:
        url: L'URL de l'image à télécharger

    Returns:
        Dict avec filename et path
    """
    try:
        # Headers pour simuler un navigateur
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "Referer": "https://www.google.com/",
        }

        # Télécharger l'image avec streaming et redirections
        response = requests.get(
            url, timeout=60, stream=True, headers=headers, allow_redirects=True
        )
        response.raise_for_status()

        # Détecter le type de contenu
        content_type = response.headers.get("content-type", "").lower()

        # Déterminer l'extension selon le type MIME
        ext_map = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
            "image/heic": ".heic",
            "image/heif": ".heif",
        }

        ext = ext_map.get(content_type)
        if not ext:
            # Essayer de détecter depuis l'URL
            if ".jpg" in url.lower() or ".jpeg" in url.lower():
                ext = ".jpg"
            elif ".png" in url.lower():
                ext = ".png"
            elif ".webp" in url.lower():
                ext = ".webp"
            elif ".heic" in url.lower():
                ext = ".heic"
            elif ".heif" in url.lower():
                ext = ".heif"
            else:
                ext = ".jpg"  # Default

        if ext not in ALLOWED_EXTENSIONS:
            raise InvalidUploadException(
                f"Format non supporté. Formats acceptés: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Lire le contenu en streaming
        content = b""
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                content += chunk
                # Vérifier la taille pendant le téléchargement
                if len(content) > MAX_FILE_SIZE_BYTES:
                    raise InvalidUploadException(
                        f"Fichier trop volumineux. Maximum: {MAX_FILE_SIZE_MB}MB"
                    )

        # Valider le contenu téléchargé
        _validate_image_content(content)

        # Convertir et compresser si nécessaire
        content, final_ext = _convert_and_compress_image(content, ext)

        # Générer un nom de fichier unique
        filename = f"{uuid.uuid4()}{final_ext}"
        filepath = UPLOAD_DIR / filename

        # Sauvegarder le fichier
        with open(filepath, "wb") as buffer:
            buffer.write(content)

        return {"filename": filename, "path": f"/uploads/{filename}"}

    except requests.exceptions.Timeout:
        raise InvalidUploadException("Le téléchargement a pris trop de temps (timeout)")
    except requests.exceptions.RequestException as e:
        raise InvalidUploadException(f"Erreur lors du téléchargement: {str(e)}")
    except Exception as e:
        raise InvalidUploadException(f"Erreur: {str(e)}")
