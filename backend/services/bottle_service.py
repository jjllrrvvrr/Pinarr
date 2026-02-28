"""Service pour la gestion des bouteilles."""

from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict, Any
import models
import schemas
from exceptions import BottleNotFoundException, MaxQuantityReachedException


def _build_position_data(pos: models.Position) -> Optional[Dict[str, Any]]:
    """Construit les données de position à partir d'un objet Position."""
    if not pos:
        return None

    row = pos.row
    col = row.column if row else None
    cave = col.cave if col else None

    return {
        "id": pos.id,
        "line": pos.line,
        "position": pos.position,
        "row_id": pos.row_id,
        "row_name": row.name if row else None,
        "column_id": col.id if col else None,
        "column_name": col.name if col else None,
        "cave_id": cave.id if cave else None,
        "cave_name": cave.name if cave else None,
        "code": pos.code,
    }


def get_bottles_with_positions(
    db: Session, skip: int = 0, limit: int = 100
) -> List[Dict[str, Any]]:
    """Récupère toutes les bouteilles avec leurs positions en une seule requête optimisée."""
    bottles = (
        db.query(models.Bottle)
        .options(
            joinedload(models.Bottle.positions)
            .joinedload(models.Position.row)
            .joinedload(models.CaveRow.column)
            .joinedload(models.CaveColumn.cave)
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []
    for bottle in bottles:
        positions_data = []
        for pos in bottle.positions:
            if pos:
                positions_data.append(_build_position_data(pos))

        result.append(
            {
                **schemas.Bottle.model_validate(bottle).model_dump(),
                "positions": positions_data,
            }
        )

    return result


def get_bottle_with_position(db: Session, bottle_id: int) -> Dict[str, Any]:
    """Récupère une bouteille avec toutes ses positions."""
    bottle = (
        db.query(models.Bottle)
        .options(
            joinedload(models.Bottle.positions)
            .joinedload(models.Position.row)
            .joinedload(models.CaveRow.column)
            .joinedload(models.CaveColumn.cave)
        )
        .filter(models.Bottle.id == bottle_id)
        .first()
    )

    if not bottle:
        raise BottleNotFoundException(f"Bottle {bottle_id} not found")

    positions_data = []
    for pos in bottle.positions:
        if pos:
            positions_data.append(_build_position_data(pos))

    return {
        **schemas.Bottle.model_validate(bottle).model_dump(),
        "positions": positions_data,
    }


def check_duplicate_bottles(db: Session, name: str, year: int) -> List[Dict[str, Any]]:
    """Vérifie si des bouteilles similaires existent déjà."""
    matches = (
        db.query(models.Bottle)
        .filter(models.Bottle.name.ilike(f"%{name}%"), models.Bottle.year == year)
        .all()
    )

    return [
        {
            "id": b.id,
            "name": b.name,
            "year": b.year,
            "domaine": b.domaine,
            "quantity": b.quantity,
        }
        for b in matches
    ]


def create_bottle(db: Session, bottle: schemas.BottleCreate) -> models.Bottle:
    """Crée une nouvelle bouteille."""
    db_bottle = models.Bottle(**bottle.model_dump())
    db.add(db_bottle)
    db.commit()
    db.refresh(db_bottle)
    return db_bottle


def update_bottle(
    db: Session, bottle_id: int, bottle_data: schemas.BottleCreate
) -> models.Bottle:
    """Met à jour une bouteille existante."""
    db_bottle = db.query(models.Bottle).filter(models.Bottle.id == bottle_id).first()
    if not db_bottle:
        raise BottleNotFoundException(f"Bottle {bottle_id} not found")

    for key, value in bottle_data.model_dump(exclude_unset=True).items():
        setattr(db_bottle, key, value)

    db.add(db_bottle)
    db.commit()
    db.refresh(db_bottle)
    return db_bottle


def patch_bottle(
    db: Session, bottle_id: int, bottle_data: schemas.BottlePatch
) -> models.Bottle:
    """Met à jour partiellement une bouteille."""
    db_bottle = db.query(models.Bottle).filter(models.Bottle.id == bottle_id).first()
    if not db_bottle:
        raise BottleNotFoundException(f"Bottle {bottle_id} not found")

    for key, value in bottle_data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(db_bottle, key, value)

    db.add(db_bottle)
    db.commit()
    db.refresh(db_bottle)
    return db_bottle


def delete_bottle(db: Session, bottle_id: int) -> None:
    """Supprime une bouteille."""
    db_bottle = db.query(models.Bottle).filter(models.Bottle.id == bottle_id).first()
    if not db_bottle:
        raise BottleNotFoundException(f"Bottle {bottle_id} not found")

    db.delete(db_bottle)
    db.commit()


def validate_bottle_placement(
    db: Session, bottle_id: int, exclude_position_id: Optional[int] = None
) -> None:
    """Vérifie que la quantité maximale n'est pas dépassée."""
    db_bottle = db.query(models.Bottle).filter(models.Bottle.id == bottle_id).first()
    if not db_bottle:
        raise BottleNotFoundException(f"Bottle {bottle_id} not found")

    query = db.query(models.Position).filter(models.Position.bottle_id == bottle_id)
    if exclude_position_id:
        query = query.filter(models.Position.id != exclude_position_id)

    existing_placements = query.count()

    if existing_placements >= db_bottle.quantity:
        raise MaxQuantityReachedException(
            f"Quantité maximale atteinte ({db_bottle.quantity})"
        )


def search_bottles_by_name(
    db: Session, query: str, limit: int = 5
) -> List[Dict[str, Any]]:
    """Recherche des bouteilles par nom (recherche partielle)."""
    bottles = (
        db.query(models.Bottle)
        .filter(models.Bottle.name.ilike(f"%{query}%"))
        .order_by(models.Bottle.name)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": b.id,
            "name": b.name,
            "year": b.year,
            "domaine": b.domaine,
            "quantity": b.quantity,
            "image_path": b.image_path,
        }
        for b in bottles
    ]
