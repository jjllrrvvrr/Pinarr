"""Service pour la gestion des bouteilles."""

from datetime import datetime
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


def _serialize_physical_bottle(pb: models.PhysicalBottle) -> Dict[str, Any]:
    """Sérialise une bouteille physique en dict."""
    return {
        "id": pb.id,
        "qr_code": pb.qr_code,
        "status": pb.status,
        "acquisition_date": pb.acquisition_date,
        "position_id": pb.position_id,
        "position_code": pb.position.code if pb.position else None,
        "cave_name": (
            pb.position.row.column.cave.name
            if pb.position and pb.position.row and pb.position.row.column
            and pb.position.row.column.cave
            else None
        ),
    }


def _serialize_position(pos: models.Position) -> Dict[str, Any]:
    """Sérialise une position en dict."""
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


def _serialize_bottle(bottle: models.Bottle) -> Dict[str, Any]:
    """Sérialise une bouteille avec ses physical_bottles et positions."""
    positions_data = []
    physical_bottles_data = []
    cellar_quantity = 0
    for pb in bottle.physical_bottles:
        if pb.status == "in_cellar":
            cellar_quantity += 1
        physical_bottles_data.append(_serialize_physical_bottle(pb))
        if pb and pb.position:
            positions_data.append(_serialize_position(pb.position))

    return {
        **schemas.Bottle.model_validate(bottle).model_dump(),
        "positions": positions_data,
        "physical_bottles": physical_bottles_data,
        "cellar_quantity": cellar_quantity,
    }


def get_bottles_with_positions(
    db: Session, skip: int = 0, limit: int = 100
) -> List[Dict[str, Any]]:
    """Récupère toutes les bouteilles avec leurs positions."""
    bottles = (
        db.query(models.Bottle)
        .options(
            joinedload(models.Bottle.physical_bottles)
            .joinedload(models.PhysicalBottle.position)
            .joinedload(models.Position.row)
            .joinedload(models.CaveRow.column)
            .joinedload(models.CaveColumn.cave)
        )
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_serialize_bottle(b) for b in bottles]


def get_bottle_with_position(db: Session, bottle_id: int) -> Dict[str, Any]:
    """Récupère une bouteille avec toutes ses positions."""
    bottle = (
        db.query(models.Bottle)
        .options(
            joinedload(models.Bottle.physical_bottles)
            .joinedload(models.PhysicalBottle.position)
            .joinedload(models.Position.row)
            .joinedload(models.CaveRow.column)
            .joinedload(models.CaveColumn.cave)
        )
        .filter(models.Bottle.id == bottle_id)
        .first()
    )

    if not bottle:
        raise BottleNotFoundException(f"Bottle {bottle_id} not found")

    return _serialize_bottle(bottle)


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
    
    # Générer automatiquement les bouteilles physiques (QR codes) si quantity > 0
    if db_bottle.quantity and db_bottle.quantity > 0:
        from services.physical_bottle_service import generate_qr_codes_for_bottle
        generate_qr_codes_for_bottle(db, db_bottle.id, db_bottle.quantity)
    
    return db_bottle


def update_bottle(
    db: Session, bottle_id: int, bottle_data: schemas.BottleCreate
) -> models.Bottle:
    """Met à jour une bouteille existante."""
    db_bottle = db.query(models.Bottle).filter(models.Bottle.id == bottle_id).first()
    if not db_bottle:
        raise BottleNotFoundException(f"Bottle {bottle_id} not found")

    data = bottle_data.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_bottle, key, value)

    db.add(db_bottle)
    db.commit()
    db.refresh(db_bottle)

    # Synchroniser les bouteilles physiques si quantity modifiée
    if "quantity" in data:
        _sync_physical_bottles(db, bottle_id, data.get("quantity"))
        db.refresh(db_bottle)

    return db_bottle


def patch_bottle(
    db: Session, bottle_id: int, bottle_data: schemas.BottlePatch
) -> models.Bottle:
    """Met à jour partiellement une bouteille."""
    db_bottle = db.query(models.Bottle).filter(models.Bottle.id == bottle_id).first()
    if not db_bottle:
        raise BottleNotFoundException(f"Bottle {bottle_id} not found")

    data = bottle_data.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_bottle, key, value)

    db.add(db_bottle)
    db.commit()
    db.refresh(db_bottle)

    # Synchroniser les bouteilles physiques si quantity modifiée
    if "quantity" in data:
        _sync_physical_bottles(db, bottle_id, data.get("quantity"))
        db.refresh(db_bottle)

    return db_bottle


def _sync_physical_bottles(db: Session, bottle_id: int, target_quantity: Optional[int]) -> None:
    """Synchronise le nombre de physical_bottles en cave avec la quantity souhaitée.

    - Si target_quantity > physical actuelles : génère des QR supplémentaires
    - Si target_quantity < physical actuelles : supprime d'abord les non-placées,
      puis consomme les placées
    """
    if target_quantity is None or target_quantity < 0:
        return

    physical_bottles = (
        db.query(models.PhysicalBottle)
        .filter(
            models.PhysicalBottle.bottle_id == bottle_id,
            models.PhysicalBottle.status == "in_cellar",
        )
        .order_by(models.PhysicalBottle.position_id.is_(None).desc(), models.PhysicalBottle.id)
        .all()
    )

    current = len(physical_bottles)

    if target_quantity > current:
        from services.physical_bottle_service import generate_qr_codes_for_bottle
        generate_qr_codes_for_bottle(db, bottle_id, target_quantity - current)

    elif target_quantity < current:
        to_remove = current - target_quantity
        removed = 0
        for pb in physical_bottles:
            if removed >= to_remove:
                break
            if pb.position_id is None:
                db.delete(pb)
                removed += 1

        for pb in physical_bottles:
            if removed >= to_remove:
                break
            if pb.position_id is not None:
                pb.status = "consumed"
                pb.removal_date = datetime.utcnow()
                pb.position_id = None
                removed += 1

        db.commit()


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
    """Vérifie qu'il reste des bouteilles physiques libres pour ce vin."""
    db_bottle = db.query(models.Bottle).filter(models.Bottle.id == bottle_id).first()
    if not db_bottle:
        raise BottleNotFoundException(f"Bottle {bottle_id} not found")

    # Compter combien de physical_bottles de ce vin sont actuellement placés
    query = (
        db.query(models.PhysicalBottle)
        .filter(
            models.PhysicalBottle.bottle_id == bottle_id,
            models.PhysicalBottle.status == "in_cellar",
            models.PhysicalBottle.position_id != None,
        )
    )
    if exclude_position_id:
        query = query.filter(
            models.PhysicalBottle.position_id != exclude_position_id
        )

    existing_placements = query.count()

    # Le plafond est le nombre total de bouteilles physiques en cave
    total_physical = (
        db.query(models.PhysicalBottle)
        .filter(
            models.PhysicalBottle.bottle_id == bottle_id,
            models.PhysicalBottle.status == "in_cellar",
        )
        .count()
    )

    if existing_placements >= total_physical:
        raise MaxQuantityReachedException(
            f"Plus de bouteille physique disponible pour ce vin (total: {total_physical})"
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
