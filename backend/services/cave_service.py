"""Service pour la gestion des caves."""

from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import models
import schemas
from exceptions import (
    CaveNotFoundException,
    ColumnNotFoundException,
    RowNotFoundException,
    PositionNotFoundException,
)


# === CAVES ===


def get_caves(db: Session) -> List[models.Cave]:
    """Récupère toutes les caves avec leurs colonnes, rangées et positions."""
    return (
        db.query(models.Cave)
        .options(
            joinedload(models.Cave.columns)
            .joinedload(models.CaveColumn.rows)
            .joinedload(models.CaveRow.positions)
        )
        .all()
    )


def get_cave(db: Session, cave_id: int) -> models.Cave:
    """Récupère une cave par son ID."""
    cave = (
        db.query(models.Cave)
        .options(
            joinedload(models.Cave.columns)
            .joinedload(models.CaveColumn.rows)
            .joinedload(models.CaveRow.positions)
        )
        .filter(models.Cave.id == cave_id)
        .first()
    )

    if not cave:
        raise CaveNotFoundException(f"Cave {cave_id} not found")

    return cave


def create_cave(db: Session, cave: schemas.CaveCreate) -> models.Cave:
    """Crée une nouvelle cave."""
    db_cave = models.Cave(name=cave.name)
    db.add(db_cave)
    db.commit()
    db.refresh(db_cave)
    return db_cave


def update_cave(db: Session, cave_id: int, cave: schemas.CaveCreate) -> models.Cave:
    """Met à jour une cave existante."""
    db_cave = db.query(models.Cave).filter(models.Cave.id == cave_id).first()
    if not db_cave:
        raise CaveNotFoundException(f"Cave {cave_id} not found")

    db_cave.name = cave.name  # type: ignore
    db.add(db_cave)
    db.commit()
    db.refresh(db_cave)
    return db_cave


def delete_cave(db: Session, cave_id: int) -> None:
    """Supprime une cave."""
    db_cave = db.query(models.Cave).filter(models.Cave.id == cave_id).first()
    if not db_cave:
        raise CaveNotFoundException(f"Cave {cave_id} not found")

    db.delete(db_cave)
    db.commit()


# === COLUMNS ===


def create_column(
    db: Session, cave_id: int, column: schemas.CaveColumnCreate
) -> models.CaveColumn:
    """Crée une nouvelle colonne dans une cave."""
    cave = db.query(models.Cave).filter(models.Cave.id == cave_id).first()
    if not cave:
        raise CaveNotFoundException(f"Cave {cave_id} not found")

    db_column = models.CaveColumn(
        cave_id=cave_id, name=column.name, order=column.order or 0
    )
    db.add(db_column)
    db.commit()
    db.refresh(db_column)
    return db_column


def update_column(
    db: Session, column_id: int, column: schemas.CaveColumnCreate
) -> models.CaveColumn:
    """Met à jour une colonne existante."""
    db_column = (
        db.query(models.CaveColumn).filter(models.CaveColumn.id == column_id).first()
    )
    if not db_column:
        raise ColumnNotFoundException(f"Column {column_id} not found")

    db_column.name = column.name  # type: ignore
    db_column.order = column.order or 0  # type: ignore
    db.add(db_column)
    db.commit()
    db.refresh(db_column)
    return db_column


def delete_column(db: Session, column_id: int) -> None:
    """Supprime une colonne."""
    db_column = (
        db.query(models.CaveColumn).filter(models.CaveColumn.id == column_id).first()
    )
    if not db_column:
        raise ColumnNotFoundException(f"Column {column_id} not found")

    db.delete(db_column)
    db.commit()


# === ROWS ===


def create_row(
    db: Session, column_id: int, row: schemas.CaveRowCreate
) -> models.CaveRow:
    """Crée une nouvelle rangée avec ses positions automatiquement générées."""
    column = (
        db.query(models.CaveColumn).filter(models.CaveColumn.id == column_id).first()
    )
    if not column:
        raise ColumnNotFoundException(f"Column {column_id} not found")

    db_row = models.CaveRow(
        column_id=column_id,
        name=row.name,
        width=row.width,
        height=row.height,
        order=row.order or 0,
    )
    db.add(db_row)
    db.commit()
    db.refresh(db_row)

    # Créer automatiquement les positions
    positions_to_create = []
    for line in range(1, row.height + 1):
        for pos in range(1, row.width + 1):
            positions_to_create.append(
                models.Position(row_id=db_row.id, line=line, position=pos)
            )

    db.add_all(positions_to_create)
    db.commit()

    return db_row


def update_row(db: Session, row_id: int, row: schemas.CaveRowCreate) -> models.CaveRow:
    """Met à jour une rangée et recrée les positions si dimensions changées."""
    db_row = db.query(models.CaveRow).filter(models.CaveRow.id == row_id).first()
    if not db_row:
        raise RowNotFoundException(f"Row {row_id} not found")

    old_width = db_row.width
    old_height = db_row.height

    db_row.name = row.name  # type: ignore
    db_row.width = row.width  # type: ignore
    db_row.height = row.height  # type: ignore
    db_row.order = row.order or 0  # type: ignore

    # Recréer les positions si dimensions changées
    if row.width != old_width or row.height != old_height:
        db.query(models.Position).filter(models.Position.row_id == row_id).delete()

        positions_to_create = []
        for line in range(1, row.height + 1):
            for pos in range(1, row.width + 1):
                positions_to_create.append(
                    models.Position(row_id=row_id, line=line, position=pos)
                )
        db.add_all(positions_to_create)

    db.add(db_row)
    db.commit()
    db.refresh(db_row)
    return db_row


def delete_row(db: Session, row_id: int) -> None:
    """Supprime une rangée."""
    db_row = db.query(models.CaveRow).filter(models.CaveRow.id == row_id).first()
    if not db_row:
        raise RowNotFoundException(f"Row {row_id} not found")

    db.delete(db_row)
    db.commit()


# === POSITIONS ===


def get_positions_for_row(db: Session, row_id: int) -> List[models.Position]:
    """Récupère toutes les positions d'une rangée avec les bouteilles associées."""
    return (
        db.query(models.Position)
        .options(joinedload(models.Position.bottle_at_position))
        .filter(models.Position.row_id == row_id)
        .all()
    )


def create_position(
    db: Session, row_id: int, position: schemas.PositionCreate
) -> models.Position:
    """Crée une nouvelle position."""
    row = db.query(models.CaveRow).filter(models.CaveRow.id == row_id).first()
    if not row:
        raise RowNotFoundException(f"Row {row_id} not found")

    db_position = models.Position(
        row_id=row_id, line=position.line, position=position.position
    )
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    return db_position


def get_or_create_position(
    db: Session, row_id: int, line: int, pos: int
) -> models.Position:
    """Récupère une position existante ou la crée si elle n'existe pas."""
    db_position = (
        db.query(models.Position)
        .filter(
            models.Position.row_id == row_id,
            models.Position.line == line,
            models.Position.position == pos,
        )
        .first()
    )

    if not db_position:
        row = db.query(models.CaveRow).filter(models.CaveRow.id == row_id).first()
        if not row:
            raise RowNotFoundException(f"Row {row_id} not found")

        db_position = models.Position(row_id=row_id, line=line, position=pos)
        db.add(db_position)
        db.commit()
        db.refresh(db_position)

    return db_position


def assign_bottle_to_position(
    db: Session, position_id: int, bottle_id: Optional[int]
) -> models.Position:
    """Assigne une bouteille à une position (ou la retire si None)."""
    db_position = (
        db.query(models.Position).filter(models.Position.id == position_id).first()
    )
    if not db_position:
        raise PositionNotFoundException(f"Position {position_id} not found")

    db_position.bottle_id = bottle_id  # type: ignore
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    return db_position


def remove_bottle_from_position(db: Session, position_id: int) -> None:
    """Retire une bouteille d'une position."""
    db_position = (
        db.query(models.Position).filter(models.Position.id == position_id).first()
    )
    if not db_position:
        raise PositionNotFoundException(f"Position {position_id} not found")

    db_position.bottle_id = None  # type: ignore
    db.add(db_position)
    db.commit()
