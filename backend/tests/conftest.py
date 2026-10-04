"""Configuration pytest pour les tests backend Pinarr.

Utilise une base SQLite temporaire isolée - ne touche jamais la DB de prod.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Isoler la DB de test AVANT tout import applicatif
_TEST_DIR = tempfile.mkdtemp(prefix="pinarr_test_")
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DIR}/test_pinarr.db"
os.environ["SECRET_KEY"] = "test-secret-key-not-for-production"

# Rediriger UPLOAD_DIR vers un dossier temporaire
_UPLOAD_DIR = Path(_TEST_DIR) / "uploads"
_UPLOAD_DIR.mkdir(exist_ok=True)

# Injecter le chemin backend
sys.path.insert(0, str(Path(__file__).parent.parent))

# config.py crée UPLOAD_DIR en dur /app/uploads à l'import ; le patcher
import config  # noqa: E402

config.UPLOAD_DIR = _UPLOAD_DIR

from database import Base, SessionLocal, engine  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Crée toutes les tables une seule fois pour la session de test."""
    # Importer models pour enregistrer les tables sur Base.metadata
    # AVANT create_all (sinon metadata est vide)
    import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()


@pytest.fixture
def db():
    """Session DB par test, avec rollback pour l'isolation."""
    session = SessionLocal()
    try:
        yield session
        session.rollback()
    finally:
        session.close()