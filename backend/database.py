# backend/database.py
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Utiliser DATABASE_URL depuis l'environnement ou valeur par défaut
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pinarr.db")

# Adapter le chemin pour Docker si nécessaire
if DATABASE_URL.startswith("sqlite:///./"):
    # Convertir chemin relatif en absolu pour Docker
    db_path = DATABASE_URL.replace("sqlite:///./", "sqlite:////app/data/")
    SQLALCHEMY_DATABASE_URL = db_path
else:
    SQLALCHEMY_DATABASE_URL = DATABASE_URL

# S'assurer que le répertoire de la base de données existe
if SQLALCHEMY_DATABASE_URL.startswith("sqlite://"):
    db_file_path = SQLALCHEMY_DATABASE_URL.replace("sqlite://", "")
    db_dir = os.path.dirname(db_file_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def create_db_tables():
    try:
        from models import (
            Bottle,
            Cave,
            CaveColumn,
            CaveRow,
            Position,
            GeocodedRegion,
            User,
        )
    except ImportError:
        from .models import (
            Bottle,
            Cave,
            CaveColumn,
            CaveRow,
            Position,
            GeocodedRegion,
            User,
        )

    Base.metadata.create_all(bind=engine)
