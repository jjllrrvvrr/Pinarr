from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import os
import uuid

try:
    from . import models, schemas
    from .database import SessionLocal, engine, create_db_tables
except ImportError:
    import models, schemas
    from database import SessionLocal, engine, create_db_tables

create_db_tables()

app = FastAPI(title="SudoWine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "Welcome to Sudo Wine Backend!"}


# === BOTTLES ===
@app.get("/bottles/", response_model=List[schemas.BottleWithPosition])
def read_bottles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bottles = db.query(models.Bottle).offset(skip).limit(limit).all()

    result = []
    for bottle in bottles:
        position_data = None
        pos = (
            db.query(models.Position)
            .options(joinedload(models.Position.row).joinedload(models.CaveRow.column))
            .filter(models.Position.bottle_id == bottle.id)
            .first()
        )
        if pos:
            row = pos.row
            col = row.column if row else None
            position_data = {
                "id": pos.id,
                "line": pos.line,
                "position": pos.position,
                "row_id": pos.row_id,
                "row_name": row.name if row else None,
                "column_name": col.name if col else None,
                "cave_name": col.cave.name if col and col.cave else None,
                "code": pos.code,
            }
        result.append(
            {
                **schemas.Bottle.model_validate(bottle).model_dump(),
                "position": position_data,
            }
        )

    return result


@app.get("/bottles/check-duplicate/")
def check_duplicate(name: str, year: int, db: Session = Depends(get_db)):
    matches = (
        db.query(models.Bottle)
        .filter(models.Bottle.name.ilike(f"%{name}%"), models.Bottle.year == year)
        .all()
    )
    return {
        "matches": [
            {
                "id": b.id,
                "name": b.name,
                "year": b.year,
                "domaine": b.domaine,
                "quantity": b.quantity,
            }
            for b in matches
        ]
    }


@app.get("/bottles/{bottle_id}", response_model=schemas.BottleWithPosition)
def read_bottle(bottle_id: int, db: Session = Depends(get_db)):
    bottle = db.query(models.Bottle).filter(models.Bottle.id == bottle_id).first()
    if bottle is None:
        raise HTTPException(status_code=404, detail="Bottle not found")

    position_data = None
    pos = (
        db.query(models.Position)
        .options(joinedload(models.Position.row).joinedload(models.CaveRow.column))
        .filter(models.Position.bottle_id == bottle_id)
        .first()
    )
    if pos:
        row = pos.row
        col = row.column if row else None
        position_data = {
            "id": pos.id,
            "line": pos.line,
            "position": pos.position,
            "row_id": pos.row_id,
            "row_name": row.name if row else None,
            "column_name": col.name if col else None,
            "cave_name": col.cave.name if col and col.cave else None,
            "code": pos.code,
        }

    return {
        **schemas.Bottle.model_validate(bottle).model_dump(),
        "position": position_data,
    }


@app.post("/bottles/", response_model=schemas.Bottle)
def create_bottle(bottle: schemas.BottleCreate, db: Session = Depends(get_db)):
    db_bottle = models.Bottle(**bottle.model_dump())
    db.add(db_bottle)
    db.commit()
    db.refresh(db_bottle)
    return db_bottle


@app.put("/bottles/{bottle_id}", response_model=schemas.Bottle)
def update_bottle(
    bottle_id: int, bottle: schemas.BottleCreate, db: Session = Depends(get_db)
):
    db_bottle = db.query(models.Bottle).filter(models.Bottle.id == bottle_id).first()
    if db_bottle is None:
        raise HTTPException(status_code=404, detail="Bottle not found")
    for key, value in bottle.model_dump(exclude_unset=True).items():
        setattr(db_bottle, key, value)
    db.add(db_bottle)
    db.commit()
    db.refresh(db_bottle)
    return db_bottle


@app.patch("/bottles/{bottle_id}", response_model=schemas.Bottle)
def patch_bottle(
    bottle_id: int, bottle: schemas.BottlePatch, db: Session = Depends(get_db)
):
    db_bottle = db.query(models.Bottle).filter(models.Bottle.id == bottle_id).first()
    if db_bottle is None:
        raise HTTPException(status_code=404, detail="Bottle not found")
    for key, value in bottle.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(db_bottle, key, value)
    db.add(db_bottle)
    db.commit()
    db.refresh(db_bottle)
    return db_bottle


@app.delete("/bottles/{bottle_id}")
def delete_bottle(bottle_id: int, db: Session = Depends(get_db)):
    db_bottle = db.query(models.Bottle).filter(models.Bottle.id == bottle_id).first()
    if db_bottle is None:
        raise HTTPException(status_code=404, detail="Bottle not found")
    db.delete(db_bottle)
    db.commit()
    return {"message": "Bottle deleted"}


# === CAVES ===
@app.get("/caves/", response_model=List[schemas.CaveWithColumns])
def read_caves(db: Session = Depends(get_db)):
    caves = (
        db.query(models.Cave)
        .options(
            joinedload(models.Cave.columns)
            .joinedload(models.CaveColumn.rows)
            .joinedload(models.CaveRow.positions)
        )
        .all()
    )
    return caves


@app.get("/caves/{cave_id}", response_model=schemas.CaveWithColumns)
def read_cave(cave_id: int, db: Session = Depends(get_db)):
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
    if cave is None:
        raise HTTPException(status_code=404, detail="Cave not found")
    return cave


@app.post("/caves/", response_model=schemas.Cave)
def create_cave(cave: schemas.CaveCreate, db: Session = Depends(get_db)):
    db_cave = models.Cave(name=cave.name)
    db.add(db_cave)
    db.commit()
    db.refresh(db_cave)
    return db_cave


@app.put("/caves/{cave_id}", response_model=schemas.Cave)
def update_cave(cave_id: int, cave: schemas.CaveCreate, db: Session = Depends(get_db)):
    db_cave = db.query(models.Cave).filter(models.Cave.id == cave_id).first()
    if db_cave is None:
        raise HTTPException(status_code=404, detail="Cave not found")
    db_cave.name = cave.name
    db.add(db_cave)
    db.commit()
    db.refresh(db_cave)
    return db_cave


@app.delete("/caves/{cave_id}")
def delete_cave(cave_id: int, db: Session = Depends(get_db)):
    db_cave = db.query(models.Cave).filter(models.Cave.id == cave_id).first()
    if db_cave is None:
        raise HTTPException(status_code=404, detail="Cave not found")
    db.delete(db_cave)
    db.commit()
    return {"message": "Cave deleted"}


# === COLUMNS ===
@app.post("/caves/{cave_id}/columns/", response_model=schemas.CaveColumn)
def create_column(
    cave_id: int, column: schemas.CaveColumnCreate, db: Session = Depends(get_db)
):
    db_column = models.CaveColumn(cave_id=cave_id, name=column.name, order=column.order)
    db.add(db_column)
    db.commit()
    db.refresh(db_column)
    return db_column


@app.put("/columns/{column_id}", response_model=schemas.CaveColumn)
def update_column(
    column_id: int, column: schemas.CaveColumnCreate, db: Session = Depends(get_db)
):
    db_column = (
        db.query(models.CaveColumn).filter(models.CaveColumn.id == column_id).first()
    )
    if db_column is None:
        raise HTTPException(status_code=404, detail="Column not found")
    db_column.name = column.name
    db_column.order = column.order
    db.add(db_column)
    db.commit()
    db.refresh(db_column)
    return db_column


@app.delete("/columns/{column_id}")
def delete_column(column_id: int, db: Session = Depends(get_db)):
    db_column = (
        db.query(models.CaveColumn).filter(models.CaveColumn.id == column_id).first()
    )
    if db_column is None:
        raise HTTPException(status_code=404, detail="Column not found")
    db.delete(db_column)
    db.commit()
    return {"message": "Column deleted"}


# === ROWS ===
@app.post("/columns/{column_id}/rows/", response_model=schemas.CaveRow)
def create_row(
    column_id: int, row: schemas.CaveRowCreate, db: Session = Depends(get_db)
):
    db_row = models.CaveRow(
        column_id=column_id,
        name=row.name,
        width=row.width,
        height=row.height,
        order=row.order,
    )
    db.add(db_row)
    db.commit()
    db.refresh(db_row)

    for line in range(1, row.height + 1):
        for pos in range(1, row.width + 1):
            position = models.Position(row_id=db_row.id, line=line, position=pos)
            db.add(position)
    db.commit()

    return db_row


@app.put("/rows/{row_id}", response_model=schemas.CaveRow)
def update_row(row_id: int, row: schemas.CaveRowCreate, db: Session = Depends(get_db)):
    db_row = db.query(models.CaveRow).filter(models.CaveRow.id == row_id).first()
    if db_row is None:
        raise HTTPException(status_code=404, detail="Row not found")

    old_width = db_row.width
    old_height = db_row.height

    db_row.name = row.name
    db_row.width = row.width
    db_row.height = row.height
    db_row.order = row.order

    if row.width != old_width or row.height != old_height:
        db.query(models.Position).filter(models.Position.row_id == row_id).delete()
        for line in range(1, row.height + 1):
            for pos in range(1, row.width + 1):
                position = models.Position(row_id=row_id, line=line, position=pos)
                db.add(position)

    db.add(db_row)
    db.commit()
    db.refresh(db_row)
    return db_row


@app.delete("/rows/{row_id}")
def delete_row(row_id: int, db: Session = Depends(get_db)):
    db_row = db.query(models.CaveRow).filter(models.CaveRow.id == row_id).first()
    if db_row is None:
        raise HTTPException(status_code=404, detail="Row not found")
    db.delete(db_row)
    db.commit()
    return {"message": "Row deleted"}


# === POSITIONS ===
@app.post("/rows/{row_id}/positions/", response_model=schemas.Position)
def create_position(
    row_id: int, position: schemas.PositionCreate, db: Session = Depends(get_db)
):
    db_row = db.query(models.CaveRow).filter(models.CaveRow.id == row_id).first()
    if db_row is None:
        raise HTTPException(status_code=404, detail="Row not found")

    db_position = models.Position(
        row_id=row_id, line=position.line, position=position.position
    )
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    return db_position


@app.get("/rows/{row_id}/positions/", response_model=List[schemas.PositionWithBottle])
def read_positions(row_id: int, db: Session = Depends(get_db)):
    positions = (
        db.query(models.Position)
        .options(joinedload(models.Position.bottle_at_position))
        .filter(models.Position.row_id == row_id)
        .all()
    )
    return positions


@app.put("/positions/{position_id}", response_model=schemas.Position)
def update_position(
    position_id: int, position: schemas.PositionUpdate, db: Session = Depends(get_db)
):
    db_position = (
        db.query(models.Position).filter(models.Position.id == position_id).first()
    )

    if db_position is None:
        position_data = position.model_dump()
        if "row_id" not in position_data:
            position_data["row_id"] = None
        if "line" not in position_data:
            position_data["line"] = None
        if "position" not in position_data:
            position_data["position"] = None

        row = (
            db.query(models.CaveRow)
            .filter(models.CaveRow.id == position_data.get("row_id"))
            .first()
        )
        if not row:
            raise HTTPException(status_code=400, detail="Row not found")

        db_position = models.Position(
            row_id=row.id,
            line=position_data.get("line"),
            position=position_data.get("position"),
        )
        db.add(db_position)
        db.commit()

    if position.bottle_id is not None:
        db_bottle = (
            db.query(models.Bottle)
            .filter(models.Bottle.id == position.bottle_id)
            .first()
        )
        if db_bottle is None:
            raise HTTPException(status_code=404, detail="Bottle not found")

        # Vérifier la quantité maximale (en excluant la position actuelle)
        existing_placements = (
            db.query(models.Position)
            .filter(
                models.Position.bottle_id == position.bottle_id,
                models.Position.id != position_id,
            )
            .count()
        )

        if existing_placements >= db_bottle.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Quantité maximale atteinte ({db_bottle.quantity})",
            )

    db_position.bottle_id = position.bottle_id
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    return db_position


@app.delete("/positions/{position_id}/bottle")
def remove_bottle_from_position(position_id: int, db: Session = Depends(get_db)):
    db_position = (
        db.query(models.Position).filter(models.Position.id == position_id).first()
    )
    if db_position is None:
        raise HTTPException(status_code=404, detail="Position not found")
    db_position.bottle_id = None
    db.add(db_position)
    db.commit()
    return {"message": "Bottle removed from position"}


# === UPLOAD ===
@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(status_code=400, detail="Invalid image format")
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as buffer:
        buffer.write(await file.read())
    return {"filename": filename, "path": f"/uploads/{filename}"}


# === GEOCODED REGIONS ===
@app.get("/geocoded-regions/", response_model=List[schemas.GeocodedRegion])
def read_geocoded_regions(db: Session = Depends(get_db)):
    return db.query(models.GeocodedRegion).all()


@app.post("/geocoded-regions/", response_model=schemas.GeocodedRegion)
def create_geocoded_region(
    region: schemas.GeocodedRegionCreate, db: Session = Depends(get_db)
):
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
