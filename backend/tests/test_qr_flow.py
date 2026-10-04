"""Tests du flux QR : création bouteille -> physical_bottles -> scan -> remove.

Couvre la régression de la PR #3 (doublons de bouteilles physiques) et le
fonctionnement des routes publiques (sans authentification).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_create_bottle_generates_physical_bottles(db):
    """create_bottle avec quantity=N doit créer exactement N physical_bottles (PR #3)."""
    from services import create_bottle, get_bottle_physical_bottles
    import models
    import schemas

    bottle_data = schemas.BottleCreate(
        name="Châteauneuf-du-Pape", domaine="Test", year=2020, quantity=3
    )
    bottle = create_bottle(db, bottle_data)

    assert bottle.id is not None
    pbs = db.query(models.PhysicalBottle).filter(
        models.PhysicalBottle.bottle_id == bottle.id
    )
    assert pbs.count() == 3, "quantity=3 doit créer exactement 3 bouteilles physiques"

    result = get_bottle_physical_bottles(db, bottle.id)
    assert len(result) == 3
    assert all(pb["status"] == "in_cellar" for pb in result)
    # Non placées : pas de position_code
    assert all(pb.get("position_code") is None for pb in result)


def test_create_bottle_zero_quantity(db):
    """quantity=0 ou None ne doit rien générer."""
    from services import create_bottle
    import models
    import schemas

    bottle = create_bottle(db, schemas.BottleCreate(name="Sans stock", quantity=0))
    pbs = db.query(models.PhysicalBottle).filter(
        models.PhysicalBottle.bottle_id == bottle.id
    )
    assert pbs.count() == 0


def test_qr_codes_unique(db):
    """Les QR codes générés doivent être uniques."""
    from services import generate_qr_codes_for_bottle
    import models

    bottle = models.Bottle(name="Test QR", quantity=None)
    db.add(bottle)
    db.commit()

    codes = generate_qr_codes_for_bottle(db, bottle.id, 10)
    assert len(codes) == 10
    assert len(set(codes)) == 10, "QR codes en doublon détectés"


def test_scan_and_remove_qr_flow(db):
    """Scan par QR puis retrait : la bouteille passe en consumed, position libérée."""
    from services import (
        create_bottle,
        get_physical_bottle_by_qr,
        get_physical_bottle_with_details,
        remove_physical_bottle,
    )
    import models
    import schemas

    bottle = create_bottle(db, schemas.BottleCreate(name="Scan Flow", quantity=1))
    pb = (
        db.query(models.PhysicalBottle)
        .filter(models.PhysicalBottle.bottle_id == bottle.id)
        .first()
    )
    assert pb is not None

    # Scan public (comme /api/scan/{qr_code})
    found = get_physical_bottle_by_qr(db, pb.qr_code)
    assert found is not None
    details = get_physical_bottle_with_details(db, found.id)
    assert details["bottle"]["name"] == "Scan Flow"
    assert details["status"] == "in_cellar"

    # QR inconnu -> None (404 côté API)
    assert get_physical_bottle_by_qr(db, "ZZZZZZZZ") is None

    # Retrait public (comme /api/remove/{qr_code})
    remove_physical_bottle(db, found.id)
    db.refresh(pb)
    assert pb.status == "consumed"
    assert pb.removal_date is not None


def test_move_physical_bottle(db):
    """Déplacement : la position occupée doit être vérifiée."""
    from services import (
        create_bottle,
        generate_qr_codes_for_bottle,
        move_physical_bottle,
    )
    from exceptions import PinarrException
    import models
    import schemas

    bottle = create_bottle(db, schemas.BottleCreate(name="Move", quantity=1))
    pb = (
        db.query(models.PhysicalBottle)
        .filter(models.PhysicalBottle.bottle_id == bottle.id)
        .first()
    )

    # Créer une cave/colonne/rangée + 2 positions
    cave = models.Cave(name="Cave test")
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

    # Placer
    move_physical_bottle(db, pb.id, p1.id)
    db.refresh(pb)
    assert pb.position_id == p1.id

    # Une deuxième bouteille physique sur la même position -> refus
    codes = generate_qr_codes_for_bottle(db, bottle.id, 1)
    pb2 = get_pb_by_qr = (
        db.query(models.PhysicalBottle).filter_by(qr_code=codes[0]).first()
    )
    try:
        move_physical_bottle(db, pb2.id, p1.id)
        assert False, "devrait refuser une position occupée"
    except PinarrException:
        pass

    # Libérer
    move_physical_bottle(db, pb.id, None)
    db.refresh(pb)
    assert pb.position_id is None