"""Configuration centralisée de l'application Pinarr."""

import os
from pathlib import Path

# Répertoire de base du projet
BASE_DIR = Path(__file__).parent

# Configuration base de données
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pinarr.db")

# Configuration uploads
UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Sécurité uploads
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
MAX_FILE_SIZE_MB = 10  # Augmenté à 10MB pour les photos mobiles
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
}

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# API
API_PREFIX = "/api/v1"
API_TITLE = "Pinarr API"
API_VERSION = "1.0.0"

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
