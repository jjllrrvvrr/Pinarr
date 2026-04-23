from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

try:
    from .database import Base
except ImportError:
    from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)



class Bottle(Base):
    __tablename__ = "bottles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    domaine = Column(String, nullable=True)
    country = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    type = Column(String, nullable=True)
    region = Column(String, nullable=True)
    cepage = Column(String, nullable=True)
    alcohol = Column(Float, nullable=True)
    size = Column(String, nullable=True, default="75cl")
    apogee_start = Column(Integer, nullable=True)
    apogee_end = Column(Integer, nullable=True)
    # Phases de développement du vin
    jeunesse_end = Column(Integer, nullable=True)  # Fin phase Jeunesse
    maturite_end = Column(Integer, nullable=True)  # Fin phase Maturité
    # NOTE: apogee_end est déjà défini plus haut (période de consommation idéale)
    buy_link = Column(String, nullable=True)
    quantity = Column(Integer, nullable=True, default=1)
    price = Column(Float, nullable=True)
    description = Column(String, nullable=True)
    rating = Column(Integer, nullable=True)
    tags = Column(String, nullable=True)
    is_favorite = Column(Boolean, nullable=True, default=False)
    image_path = Column(String, nullable=True)

    physical_bottles = relationship(
        "PhysicalBottle", back_populates="bottle", cascade="all, delete-orphan"
    )
    # Compatibilité : positions dans la cave via les physical_bottles
    # Positions accessibles via les physical_bottles


class Cave(Base):
    __tablename__ = "caves"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    columns = relationship(
        "CaveColumn", back_populates="cave", cascade="all, delete-orphan"
    )


class CaveColumn(Base):
    __tablename__ = "cave_columns"

    id = Column(Integer, primary_key=True, index=True)
    cave_id = Column(Integer, ForeignKey("caves.id"), nullable=False)
    name = Column(String, nullable=False)
    order = Column(Integer, default=0)

    cave = relationship("Cave", back_populates="columns")
    rows = relationship(
        "CaveRow", back_populates="column", cascade="all, delete-orphan"
    )


class CaveRow(Base):
    __tablename__ = "cave_rows"

    id = Column(Integer, primary_key=True, index=True)
    column_id = Column(Integer, ForeignKey("cave_columns.id"), nullable=False)
    name = Column(String, nullable=False)
    width = Column(Integer, nullable=False, default=6)
    height = Column(Integer, nullable=False, default=4)
    order = Column(Integer, default=0)

    column = relationship("CaveColumn", back_populates="rows")
    positions = relationship(
        "Position", back_populates="row", cascade="all, delete-orphan"
    )

    @property
    def total_positions(self):
        return self.width * self.height


class PhysicalBottle(Base):
    __tablename__ = "physical_bottles"

    id = Column(Integer, primary_key=True, index=True)
    bottle_id = Column(Integer, ForeignKey("bottles.id"), nullable=False)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=True)
    qr_code = Column(String(8), unique=True, index=True, nullable=False)
    status = Column(String(20), default="in_cellar")  # in_cellar, consumed
    acquisition_date = Column(DateTime, default=datetime.utcnow)
    removal_date = Column(DateTime, nullable=True)
    notes = Column(String(500), nullable=True)

    bottle = relationship("Bottle", back_populates="physical_bottles")
    position = relationship(
        "Position",
        back_populates="physical_bottle",
        foreign_keys=[position_id]
    )


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    row_id = Column(Integer, ForeignKey("cave_rows.id"), nullable=False)
    line = Column(Integer, nullable=False)
    position = Column(Integer, nullable=False)

    row = relationship("CaveRow", back_populates="positions")
    physical_bottle = relationship(
        "PhysicalBottle",
        back_populates="position",
        uselist=False
    )

    @property
    def bottle_at_position(self):
        """Compatibilité: retourne la bouteille (Bottle) à cette position via physical_bottle."""
        return self.physical_bottle.bottle if self.physical_bottle else None

    @property
    def bottle_id(self):
        """Compatibilité: retourne directement l'ID de la bouteille assignée, via physical_bottle."""
        return self.physical_bottle.bottle_id if self.physical_bottle else None

    @property
    def code(self):
        row_name = self.row.name if self.row else "?"
        col_name = self.row.column.name if self.row and self.row.column else "?"
        return f"{col_name}-{row_name}-L{self.line}-P{self.position}"


class GeocodedRegion(Base):
    __tablename__ = "geocoded_regions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
