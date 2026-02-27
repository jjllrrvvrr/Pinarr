"""Configuration centralisée de l'application Pinarr."""

import os
from pathlib import Path

# Répertoire de base du projet
BASE_DIR = Path(__file__).parent

# Configuration base de données
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pinarr.db")

# Configuration uploads
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Sécurité uploads
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# API
API_PREFIX = "/api/v1"
API_TITLE = "Pinarr API"
API_VERSION = "1.0.0"

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
