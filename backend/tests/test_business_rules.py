"""Tests des nouvelles règles métier (phase A/B/D).

- Consommation décrémente quantity (plus de "résurrection")
- Sync transactionnel quantity <-> physical_bottles
- move/swap atomiques
- Gardes sur suppression cave/colonne/rangée occupées
- Validations pydantic
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


def _make_cave_with_positions(db):
    """Fixture utilitaire : 1 cave, 1 colonne, 1 rangée 2x1 (2 positions)."""
    import models

    cave = models.Cave(name="Cave T")
    db.add(cave)
    db.flush()
    col = models.CaveColumn(cave_id=cave.id, name="A")
    db.add(col)
    db.flush()
    row = models.CaveRow(column_id=col.id, name="R1", width=2, height=1)
    db.add(row)
    db.flush()
    p1 = models.Position(row_id=row.id, line=1, position=1)
    p2 = models.Position(row_id=row.id, line=1, position=2)
    db.add_all([p1, p2])
    db.commit()
    return cave, col, row, p1, p2


def _place_bottle_at(db, position, name="Vin"):
    """Crée un vin qty=1 et place sa physical_bottle sur la position."""
    from services import create_bottle, move_physical_bottle
    import models
    import schemas

    bottle = create_bottle(db, schemas.BottleCreate(name=name, quantity=1))
    pb = (
        db.query(models.PhysicalBottle)
        .filter(models.PhysicalBottle.bottle_id == bottle.id)
        .first()
    )
    move_physical_bottle(db, pb.id, position.id)
    return bottle, pb


def test_consume_decrements_quantity(db):
    """Bug P0 : consommer doit décrémenter Bottle.quantity."""
    from services import create_bottle, consume_physical_bottle
    import models
    import schemas

    bottle = create_bottle(db, schemas.BottleCreate(name="Dec", quantity=2))
    pb = (
        db.query(models.PhysicalBottle)
        .filter(models.PhysicalBottle.bottle_id == bottle.id)
        .first()
    )
    assert bottle.quantity == 2

    consume_physical_bottle(db, pb)
    db.commit()
    db.refresh(bottle)

    assert pb.status == "consumed"
    assert pb.position_id is None
    assert bottle.quantity == 1, "quantity doit être décrémentée"


def test_no_resurrection_after_consume(db):
    """Bug P0 : après consommation, une ré-édition cohérente ne doit pas
    générer de QR neuf (la bouteille bue ne "ressuscite" pas)."""
    from services import create_bottle, patch_bottle, consume_physical_bottle
    import models
    import schemas

    bottle = create_bottle(db, schemas.BottleCreate(name="Res", quantity=2))
    pb = (
        db.query(models.PhysicalBottle)
        .filter(models.PhysicalBottle.bottle_id == bottle.id)
        .first()
    )
    consume_physical_bottle(db, pb)
    db.commit()
    db.refresh(bottle)
    assert bottle.quantity == 1

    # Ré-édition avec la valeur à jour (= cellar_quantity) : aucun effet
    patch_bottle(db, bottle.id, schemas.BottlePatch(quantity=1))
    db.refresh(bottle)

    in_cellar = (
        db.query(models.PhysicalBottle)
        .filter(
            models.PhysicalBottle.bottle_id == bottle.id,
            models.PhysicalBottle.status == "in_cellar",
        )
        .count()
    )
    assert in_cellar == 1, "aucun QR neuf ne doit être généré"
    assert bottle.quantity == 1


def test_qr_remove_decrements_quantity(db):
    """Le flux QR public (/api/remove) doit aussi décrémenter quantity."""
    from services import create_bottle, remove_physical_bottle
    import models
    import schemas

    bottle = create_bottle(db, schemas.BottleCreate(name="QR", quantity=1))
    pb = (
        db.query(models.PhysicalBottle)
        .filter(models.PhysicalBottle.bottle_id == bottle.id)
        .first()
    )

    remove_physical_bottle(db, pb.id)
    db.refresh(bottle)
    assert bottle.quantity == 0
    assert pb.status == "consumed"


def test_sync_down_keeps_placed_for_last(db):
    """Réduire quantity consomme d'abord les non-placées (choix conservé)."""
    from services import create_bottle, patch_bottle, move_physical_bottle
    import models
    import schemas

    bottle = create_bottle(db, schemas.BottleCreate(name="Sync", quantity=3))
    cave, col, row, p1, p2 = _make_cave_with_positions(db)
    pbs = (
        db.query(models.PhysicalBottle)
        .filter(
            models.PhysicalBottle.bottle_id == bottle.id,
            models.PhysicalBottle.status == "in_cellar",
        )
        .order_by(models.PhysicalBottle.id)
        .all()
    )
    # Placer la première sur p1
    move_physical_bottle(db, pbs[0].id, p1.id)

    # Réduire à 1 : les 2 non-placées doivent être consommées, la placée reste
    patch_bottle(db, bottle.id, schemas.BottlePatch(quantity=1))
    db.refresh(bottle)
    db.refresh(pbs[0])

    assert pbs[0].position_id == p1.id, "la placée doit rester en place"
    assert pbs[1].status == "consumed"
    assert pbs[2].status == "consumed"
    assert bottle.quantity == 1


def test_move_atomic(db):
    """Move atomique : cible occupée -> l'existante repart en stock libre."""
    from services import create_bottle, move_bottle_to_position
    import models

    cave, col, row, p1, p2 = _make_cave_with_positions(db)
    b1, pb1 = _place_bottle_at(db, p1, "Vin A")
    b2, pb2 = _place_bottle_at(db, p2, "Vin B")

    move_bottle_to_position(db, p1.id, p2.id)
    db.refresh(pb1)
    db.refresh(pb2)

    assert pb1.position_id == p2.id
    assert pb2.position_id is None, "l'occupante repart en stock libre"
    assert pb2.status == "in_cellar"


def test_swap_atomic(db):
    """Swap atomique : les deux bouteilles échangent leurs positions."""
    from services import create_bottle, swap_positions
    import models

    cave, col, row, p1, p2 = _make_cave_with_positions(db)
    b1, pb1 = _place_bottle_at(db, p1, "Vin A")
    b2, pb2 = _place_bottle_at(db, p2, "Vin B")

    swap_positions(db, p1.id, p2.id)
    db.refresh(pb1)
    db.refresh(pb2)

    assert pb1.position_id == p2.id
    assert pb2.position_id == p1.id


def test_swap_with_empty_position(db):
    """Swap vers une position vide = move simple."""
    from services import swap_positions

    cave, col, row, p1, p2 = _make_cave_with_positions(db)
    b1, pb1 = _place_bottle_at(db, p1, "Vin A")

    swap_positions(db, p1.id, p2.id)
    db.refresh(pb1)
    assert pb1.position_id == p2.id


def test_delete_occupied_row_refused(db):
    """Garde : suppression d'une rangée occupée -> 400."""
    from services import delete_row
    from exceptions import PinarrException

    cave, col, row, p1, p2 = _make_cave_with_positions(db)
    _place_bottle_at(db, p1)

    with pytest.raises(PinarrException):
        delete_row(db, row.id)


def test_delete_empty_row_ok(db):
    """Rangée vide : suppression OK."""
    from services import delete_row

    cave, col, row, p1, p2 = _make_cave_with_positions(db)
    delete_row(db, row.id)  # ne doit pas lever


def test_delete_occupied_cave_and_column_refused(db):
    """Gardes : suppression cave/colonne occupées -> 400."""
    from services import delete_cave, delete_column
    from exceptions import PinarrException

    cave, col, row, p1, p2 = _make_cave_with_positions(db)
    _place_bottle_at(db, p1)

    with pytest.raises(PinarrException):
        delete_column(db, col.id)
    with pytest.raises(PinarrException):
        delete_cave(db, cave.id)


def test_validation_rating_and_quantity(db):
    """Validations pydantic : rating>5 et quantity négative rejetés (422)."""
    import schemas
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        schemas.BottleCreate(name="X", rating=99)
    with pytest.raises(ValidationError):
        schemas.BottleCreate(name="X", quantity=-3)
    with pytest.raises(ValidationError):
        schemas.BottleCreate(name="X", price=-10)
    with pytest.raises(ValidationError):
        schemas.BottleCreate(name="X", year=99999)
    with pytest.raises(ValidationError):
        schemas.BottleCreate(name="", quantity=1)  # nom vide
    with pytest.raises(ValidationError):
        schemas.BottleCreate(
            name="X", apogee_start=2030, apogee_end=2020
        )
    # Cas valides
    schemas.BottleCreate(name="OK", quantity=3, rating=5, price=19.99, year=2020)


def test_update_quantity_keeps_stock_coherent(db):
    """PATCH quantity=0 consomme tout ; quantity=3 regénère."""
    from services import create_bottle, patch_bottle
    import models
    import schemas

    bottle = create_bottle(db, schemas.BottleCreate(name="Coherent", quantity=2))

    patch_bottle(db, bottle.id, schemas.BottlePatch(quantity=0))
    db.refresh(bottle)
    in_cellar = (
        db.query(models.PhysicalBottle)
        .filter(
            models.PhysicalBottle.bottle_id == bottle.id,
            models.PhysicalBottle.status == "in_cellar",
        )
        .count()
    )
    assert in_cellar == 0
    assert bottle.quantity == 0

    patch_bottle(db, bottle.id, schemas.BottlePatch(quantity=3))
    db.refresh(bottle)
    in_cellar = (
        db.query(models.PhysicalBottle)
        .filter(
            models.PhysicalBottle.bottle_id == bottle.id,
            models.PhysicalBottle.status == "in_cellar",
        )
        .count()
    )
    assert in_cellar == 3
    assert bottle.quantity == 3