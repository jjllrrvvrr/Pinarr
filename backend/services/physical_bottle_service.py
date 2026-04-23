"""Service pour la gestion des bouteilles physiques avec QR codes."""

from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import uuid
import models
import schemas
from exceptions import BottleNotFoundException, PhysicalBottleNotFoundException, PinarrException


def generate_qr_code() -> str:
    """Génère un code QR unique de 8 caractères alphanumériques."""
    return str(uuid.uuid4())[:8].upper()


def get_physical_bottle_by_qr(
    db: Session, qr_code: str
) -> Optional[models.PhysicalBottle]:
    """Récupère une bouteille physique par son code QR."""
    return (
        db.query(models.PhysicalBottle)
        .filter(models.PhysicalBottle.qr_code == qr_code)
        .first()
    )


def get_physical_bottle_with_details(
    db: Session, physical_bottle_id: int
) -> Dict[str, Any]:
    """Récupère une bouteille physique avec toutes les infos du vin et sa position."""
    physical_bottle = (
        db.query(models.PhysicalBottle)
        .filter(models.PhysicalBottle.id == physical_bottle_id)
        .first()
    )

    if not physical_bottle:
        raise PhysicalBottleNotFoundException(
            f"Bouteille physique {physical_bottle_id} non trouvée"
        )

    # Construire la réponse
    result = {
        "id": physical_bottle.id,
        "qr_code": physical_bottle.qr_code,
        "status": physical_bottle.status,
        "acquisition_date": physical_bottle.acquisition_date,
        "removal_date": physical_bottle.removal_date,
        "notes": physical_bottle.notes,
        "bottle": None,
        "position": None,
    }

    # Ajouter les infos du vin
    if physical_bottle.bottle:
        bottle = physical_bottle.bottle
        result["bottle"] = {
            "id": bottle.id,
            "name": bottle.name,
            "domaine": bottle.domaine,
            "year": bottle.year,
            "type": bottle.type,
            "region": bottle.region,
            "cepage": bottle.cepage,
            "alcohol": bottle.alcohol,
            "size": bottle.size,
            "apogee_start": bottle.apogee_start,
            "apogee_end": bottle.apogee_end,
            "jeunesse_end": bottle.jeunesse_end,
            "maturite_end": bottle.maturite_end,
            "price": bottle.price,
            "description": bottle.description,
            "rating": bottle.rating,
            "image_path": bottle.image_path,
        }

    # Ajouter les infos de position
    if physical_bottle.position:
        pos = physical_bottle.position
        position_data = {
            "id": pos.id,
            "code": pos.code,
            "line": pos.line,
            "position": pos.position,
        }

        # Ajouter les infos de la cave
        if pos.row:
            row = pos.row
            position_data["row_name"] = row.name
            if row.column:
                col = row.column
                position_data["column_name"] = col.name
                if col.cave:
                    position_data["cave_name"] = col.cave.name
                    position_data["cave_id"] = col.cave.id

        result["position"] = position_data

    return result


def get_bottle_physical_bottles(db: Session, bottle_id: int) -> List[Dict[str, Any]]:
    """Récupère toutes les bouteilles physiques d'un vin."""
    physical_bottles = (
        db.query(models.PhysicalBottle)
        .filter(models.PhysicalBottle.bottle_id == bottle_id)
        .order_by(models.PhysicalBottle.acquisition_date.desc())
        .all()
    )

    result = []
    for pb in physical_bottles:
        item = {
            "id": pb.id,
            "qr_code": pb.qr_code,
            "status": pb.status,
            "acquisition_date": pb.acquisition_date,
            "removal_date": pb.removal_date,
        }

        if pb.position:
            item["position_code"] = pb.position.code
            if pb.position.row:
                item["row_name"] = pb.position.row.name
                if pb.position.row.column:
                    item["column_name"] = pb.position.row.column.name
                    if pb.position.row.column.cave:
                        item["cave_name"] = pb.position.row.column.cave.name
                        item["cave_id"] = pb.position.row.column.cave.id

        result.append(item)

    return result


def generate_qr_codes_for_bottle(db: Session, bottle_id: int, count: int) -> List[str]:
    """Génère N codes QR pour un vin et crée les bouteilles physiques."""
    # Vérifier que le vin existe
    bottle = db.query(models.Bottle).filter(models.Bottle.id == bottle_id).first()
    if not bottle:
        raise BottleNotFoundException(f"Vin {bottle_id} non trouvé")

    qr_codes = []

    for _ in range(count):
        # Générer un code QR unique
        qr_code = generate_qr_code()
        while (
            db.query(models.PhysicalBottle)
            .filter(models.PhysicalBottle.qr_code == qr_code)
            .first()
        ):
            qr_code = generate_qr_code()

        # Créer la bouteille physique
        physical_bottle = models.PhysicalBottle(
            bottle_id=bottle_id,
            qr_code=qr_code,
            status="in_cellar",
        )
        db.add(physical_bottle)
        db.flush()  # Pour obtenir l'ID

        qr_codes.append(qr_code)

    db.commit()
    return qr_codes


def remove_physical_bottle(db: Session, physical_bottle_id: int) -> None:
    """Retire une bouteille de la cave (marque comme consommée)."""
    physical_bottle = (
        db.query(models.PhysicalBottle)
        .filter(models.PhysicalBottle.id == physical_bottle_id)
        .first()
    )

    if not physical_bottle:
        raise PhysicalBottleNotFoundException(
            f"Bouteille physique {physical_bottle_id} non trouvée"
        )

    # Mettre à jour le statut
    physical_bottle.status = "consumed"
    physical_bottle.removal_date = datetime.utcnow()

    # Libérer la position
    if physical_bottle.position:
        physical_bottle.position_id = None

    db.commit()


def move_physical_bottle(
    db: Session, physical_bottle_id: int, position_id: Optional[int]
) -> None:
    """Déplace une bouteille physique vers une nouvelle position."""
    physical_bottle = (
        db.query(models.PhysicalBottle)
        .filter(models.PhysicalBottle.id == physical_bottle_id)
        .first()
    )

    if not physical_bottle:
        raise PhysicalBottleNotFoundException(
            f"Bouteille physique {physical_bottle_id} non trouvée"
        )

    # Libérer l'ancienne position
    if physical_bottle.position:
        physical_bottle.position_id = None

    # Assigner la nouvelle position
    if position_id:
        new_position = (
            db.query(models.Position).filter(models.Position.id == position_id).first()
        )

        if new_position:
            # Vérifier que la position n'est pas déjà occupée
            if (
                new_position.physical_bottle
                and new_position.physical_bottle.id != physical_bottle_id
            ):
                raise PinarrException(f"La position {new_position.code} est déjà occupée")

            physical_bottle.position_id = position_id
    else:
        physical_bottle.position_id = None

    db.commit()


def get_physical_bottle_count_in_cellar(db: Session, bottle_id: int) -> int:
    """Retourne le nombre de bouteilles physiques en cave pour un vin."""
    return (
        db.query(models.PhysicalBottle)
        .filter(
            models.PhysicalBottle.bottle_id == bottle_id,
            models.PhysicalBottle.status == "in_cellar",
        )
        .count()
    )
