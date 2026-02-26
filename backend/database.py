# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sudo_wine.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def create_db_tables():
    try:
        from .models import Bottle, Cave, CaveColumn, CaveRow, Position, GeocodedRegion
    except ImportError:
        from models import Bottle, Cave, CaveColumn, CaveRow, Position, GeocodedRegion

    Base.metadata.create_all(bind=engine)
