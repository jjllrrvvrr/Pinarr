"""Service pour la gestion des régions géocodées."""

from sqlalchemy.orm import Session
from typing import List
import models
import schemas


def get_geocoded_regions(db: Session) -> List[models.GeocodedRegion]:
    """Récupère toutes les régions géocodées."""
    return db.query(models.GeocodedRegion).all()


def create_geocoded_region(
    db: Session, region: schemas.GeocodedRegionCreate
) -> models.GeocodedRegion:
    """Crée une région géocodée ou retourne une existante."""
    existing = (
        db.query(models.GeocodedRegion)
        .filter(models.GeocodedRegion.name == region.name)
        .first()
    )
    if existing:
        return existing

    db_region = models.GeocodedRegion(**region.model_dump())
    db.add(db_region)
    db.commit()
    db.refresh(db_region)
    return db_region
