"""
SudoWine API - Routes FastAPI refactorisées.

Ce module utilise une architecture en services pour une meilleure maintenabilité.
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List

from config import API_TITLE, CORS_ORIGINS, UPLOAD_DIR
from database import create_db_tables, engine
from dependencies import get_db
from exceptions import SudoWineException, handle_sudowine_exception
import schemas
from services import (
    # Bottle services
    get_bottles_with_positions,
    get_bottle_with_position,
    check_duplicate_bottles,
    create_bottle,
    update_bottle,
    patch_bottle,
    delete_bottle,
    validate_bottle_placement,
    # Cave services
    get_caves,
    get_cave,
    create_cave,
    update_cave,
    delete_cave,
    create_column,
    update_column,
    delete_column,
    create_row,
    update_row,
    delete_row,
    get_positions_for_row,
    create_position,
    get_or_create_position,
    remove_bottle_from_position,
    # Upload service
    upload_image,
)
from services.geo_service import get_geocoded_regions, create_geocoded_region

# Création des tables
# create_db_tables()  # Désactivé temporairement

# Initialisation FastAPI
app = FastAPI(title=API_TITLE)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Gestionnaire d'exceptions
@app.exception_handler(SudoWineException)
async def custom_exception_handler(request, exc):
    raise handle_sudowine_exception(exc)


# Static files pour les uploads
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.get("/")
def read_root():
    """Route racine de l'API."""
    return {"message": "Welcome to Sudo Wine Backend!", "version": "1.0.0"}


# === BOTTLES ===


@app.get("/bottles/", response_model=List[schemas.BottleWithPosition])
def read_bottles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupère toutes les bouteilles avec leurs positions."""
    return get_bottles_with_positions(db, skip=skip, limit=limit)


@app.get("/bottles/check-duplicate/")

@app.get("/bottles/search/")
def search_bottles(q: str = "", limit: int = 5, db: Session = Depends(get_db)):
    """Recherche des bouteilles par nom."""
    from services.bottle_service import search_bottles_by_name
    results = search_bottles_by_name(db, q, limit)
    return {"results": results}
def check_duplicate(name: str, year: int, db: Session = Depends(get_db)):
    """Vérifie si des bouteilles similaires existent."""
    matches = check_duplicate_bottles(db, name, year)
    return {"matches": matches}


@app.get("/bottles/{bottle_id}", response_model=schemas.BottleWithPosition)
def read_bottle(bottle_id: int, db: Session = Depends(get_db)):
    """Récupère une bouteille spécifique avec sa position."""
    try:
        return get_bottle_with_position(db, bottle_id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise


@app.post("/bottles/", response_model=schemas.Bottle)
def create_bottle_endpoint(bottle: schemas.BottleCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle bouteille."""
    return create_bottle(db, bottle)


@app.put("/bottles/{bottle_id}", response_model=schemas.Bottle)
def update_bottle_endpoint(
    bottle_id: int, bottle: schemas.BottleCreate, db: Session = Depends(get_db)
):
    """Met à jour une bouteille existante."""
    try:
        return update_bottle(db, bottle_id, bottle)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise


@app.patch("/bottles/{bottle_id}", response_model=schemas.Bottle)
def patch_bottle_endpoint(
    bottle_id: int, bottle: schemas.BottlePatch, db: Session = Depends(get_db)
):
    """Met à jour partiellement une bouteille."""
    try:
        return patch_bottle(db, bottle_id, bottle)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise


@app.delete("/bottles/{bottle_id}")
def delete_bottle_endpoint(bottle_id: int, db: Session = Depends(get_db)):
    """Supprime une bouteille."""
    try:
        delete_bottle(db, bottle_id)
        return {"message": "Bottle deleted successfully"}
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise


# === CAVES ===


@app.get("/caves/", response_model=List[schemas.CaveWithColumns])
def read_caves(db: Session = Depends(get_db)):
    """Récupère toutes les caves avec leur structure complète."""
    return get_caves(db)


@app.get("/caves/{cave_id}", response_model=schemas.CaveWithColumns)
def read_cave(cave_id: int, db: Session = Depends(get_db)):
    """Récupère une cave spécifique."""
    try:
        return get_cave(db, cave_id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise


@app.post("/caves/", response_model=schemas.Cave)
def create_cave_endpoint(cave: schemas.CaveCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle cave."""
    return create_cave(db, cave)


@app.put("/caves/{cave_id}", response_model=schemas.Cave)
def update_cave_endpoint(
    cave_id: int, cave: schemas.CaveCreate, db: Session = Depends(get_db)
):
    """Met à jour une cave existante."""
    try:
        return update_cave(db, cave_id, cave)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise


@app.delete("/caves/{cave_id}")
def delete_cave_endpoint(cave_id: int, db: Session = Depends(get_db)):
    """Supprime une cave."""
    try:
        delete_cave(db, cave_id)
        return {"message": "Cave deleted successfully"}
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise


# === COLUMNS ===


@app.post("/caves/{cave_id}/columns/", response_model=schemas.CaveColumn)
def create_column_endpoint(
    cave_id: int, column: schemas.CaveColumnCreate, db: Session = Depends(get_db)
):
    """Crée une nouvelle colonne dans une cave."""
    try:
        return create_column(db, cave_id, column)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise


@app.put("/columns/{column_id}", response_model=schemas.CaveColumn)
def update_column_endpoint(
    column_id: int, column: schemas.CaveColumnCreate, db: Session = Depends(get_db)
):
    """Met à jour une colonne existante."""
    try:
        return update_column(db, column_id, column)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise


@app.delete("/columns/{column_id}")
def delete_column_endpoint(column_id: int, db: Session = Depends(get_db)):
    """Supprime une colonne."""
    try:
        delete_column(db, column_id)
        return {"message": "Column deleted successfully"}
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise


# === ROWS ===


@app.post("/columns/{column_id}/rows/", response_model=schemas.CaveRow)
def create_row_endpoint(
    column_id: int, row: schemas.CaveRowCreate, db: Session = Depends(get_db)
):
    """Crée une nouvelle rangée avec positions automatiques."""
    try:
        return create_row(db, column_id, row)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise


@app.put("/rows/{row_id}", response_model=schemas.CaveRow)
def update_row_endpoint(
    row_id: int, row: schemas.CaveRowCreate, db: Session = Depends(get_db)
):
    """Met à jour une rangée et recrée les positions si nécessaire."""
    try:
        return update_row(db, row_id, row)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise


@app.delete("/rows/{row_id}")
def delete_row_endpoint(row_id: int, db: Session = Depends(get_db)):
    """Supprime une rangée."""
    try:
        delete_row(db, row_id)
        return {"message": "Row deleted successfully"}
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise


# === POSITIONS ===


@app.post("/rows/{row_id}/positions/", response_model=schemas.Position)
def create_position_endpoint(
    row_id: int, position: schemas.PositionCreate, db: Session = Depends(get_db)
):
    """Crée une nouvelle position dans une rangée."""
    try:
        return create_position(db, row_id, position)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise


@app.get("/rows/{row_id}/positions/", response_model=List[schemas.PositionWithBottle])
def read_positions(row_id: int, db: Session = Depends(get_db)):
    """Récupère toutes les positions d'une rangée avec leurs bouteilles."""
    return get_positions_for_row(db, row_id)


@app.put("/positions/{position_id}", response_model=schemas.Position)
def update_position(
    position_id: int, position: schemas.PositionUpdate, db: Session = Depends(get_db)
):
    """Met à jour une position et assigne une bouteille si spécifiée."""
    from services import assign_bottle_to_position

    # Vérifier la quantité maximale
    if position.bottle_id is not None:
        try:
            validate_bottle_placement(
                db, position.bottle_id, exclude_position_id=position_id
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    try:
        db_position = assign_bottle_to_position(db, position_id, position.bottle_id)
        return db_position
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise


@app.delete("/positions/{position_id}/bottle")
def remove_bottle_from_position_endpoint(
    position_id: int, db: Session = Depends(get_db)
):
    """Retire une bouteille d'une position."""
    try:
        remove_bottle_from_position(db, position_id)
        return {"message": "Bottle removed from position"}
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise


# === UPLOAD ===


@app.post("/upload/")
async def upload_image_endpoint(file: UploadFile = File(...)):
    """Upload une image avec validation complète."""
    try:
        return upload_image(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# === GEOCODED REGIONS ===


@app.get("/geocoded-regions/", response_model=List[schemas.GeocodedRegion])
def read_geocoded_regions(db: Session = Depends(get_db)):
    """Récupère toutes les régions géocodées."""
    return get_geocoded_regions(db)


@app.post("/geocoded-regions/", response_model=schemas.GeocodedRegion)
def create_geocoded_region_endpoint(
    region: schemas.GeocodedRegionCreate, db: Session = Depends(get_db)
):
    """Crée ou retourne une région géocodée existante."""
    return create_geocoded_region(db, region)
