from pydantic import BaseModel
from typing import Optional, List
from pydantic import ConfigDict


class BottleBase(BaseModel):
    name: str
    domaine: Optional[str] = None
    country: Optional[str] = None
    year: Optional[int] = None
    type: Optional[str] = None
    region: Optional[str] = None
    cepage: Optional[str] = None
    alcohol: Optional[float] = None
    size: Optional[str] = "75cl"
    apogee_start: Optional[int] = None
    apogee_end: Optional[int] = None
    buy_link: Optional[str] = None
    quantity: Optional[int] = 1
    price: Optional[float] = None
    description: Optional[str] = None
    rating: Optional[int] = None
    tags: Optional[str] = None
    is_favorite: Optional[bool] = False
    image_path: Optional[str] = None


class BottleCreate(BottleBase):
    pass


class BottlePatch(BaseModel):
    name: Optional[str] = None
    domaine: Optional[str] = None
    country: Optional[str] = None
    year: Optional[int] = None
    type: Optional[str] = None
    region: Optional[str] = None
    cepage: Optional[str] = None
    alcohol: Optional[float] = None
    size: Optional[str] = None
    apogee_start: Optional[int] = None
    apogee_end: Optional[int] = None
    buy_link: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    description: Optional[str] = None
    rating: Optional[int] = None
    tags: Optional[str] = None
    is_favorite: Optional[bool] = None
    image_path: Optional[str] = None


class Bottle(BottleBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class BottleSummary(BaseModel):
    id: int
    name: str
    domaine: Optional[str] = None
    country: Optional[str] = None
    year: Optional[int] = None
    type: Optional[str] = None
    region: Optional[str] = None
    price: Optional[float] = None
    rating: Optional[int] = None
    size: Optional[str] = None
    apogee_start: Optional[int] = None
    apogee_end: Optional[int] = None
    image_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class BottleWithPosition(Bottle):
    positions: List[dict] = []

    model_config = ConfigDict(from_attributes=True)


class CaveBase(BaseModel):
    name: str


class CaveCreate(CaveBase):
    pass


class Cave(CaveBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CaveWithColumns(Cave):
    columns: List["CaveColumnWithRows"] = []

    model_config = ConfigDict(from_attributes=True)


class CaveColumnBase(BaseModel):
    name: str
    order: Optional[int] = 0


class CaveColumnCreate(CaveColumnBase):
    pass


class CaveColumn(CaveColumnBase):
    id: int
    cave_id: int

    model_config = ConfigDict(from_attributes=True)


class CaveColumnWithRows(CaveColumn):
    rows: List["CaveRowWithPositions"] = []

    model_config = ConfigDict(from_attributes=True)


class CaveRowBase(BaseModel):
    name: str
    width: int = 6
    height: int = 4
    order: Optional[int] = 0


class CaveRowCreate(CaveRowBase):
    pass


class CaveRow(CaveRowBase):
    id: int
    column_id: int

    model_config = ConfigDict(from_attributes=True)


class CaveRowWithPositions(CaveRow):
    positions: List["PositionWithBottle"] = []

    model_config = ConfigDict(from_attributes=True)


class PositionBase(BaseModel):
    line: int
    position: int


class PositionCreate(PositionBase):
    pass


class Position(PositionBase):
    id: int
    row_id: int
    line: int
    position: int
    bottle_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class PositionWithBottle(Position):
    bottle_at_position: Optional[BottleSummary] = None

    model_config = ConfigDict(from_attributes=True)


class PositionUpdate(BaseModel):
    bottle_id: Optional[int] = None
    row_id: Optional[int] = None
    line: Optional[int] = None
    position: Optional[int] = None


class GeocodedRegionBase(BaseModel):
    name: str
    lat: float
    lon: float


class GeocodedRegionCreate(GeocodedRegionBase):
    pass


class GeocodedRegion(GeocodedRegionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
