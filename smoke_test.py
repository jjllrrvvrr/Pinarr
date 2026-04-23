import sys
sys.path.insert(0, '/app/backend')

print("=== Import Check ===", flush=True)
from services import (
    get_bottles_with_positions,
    get_bottle_with_position,
    create_bottle,
    patch_bottle,
    delete_bottle,
    validate_bottle_placement,
    get_caves,
    create_cave,
    create_column,
    create_row,
    create_position,
    assign_bottle_to_position,
    remove_bottle_from_position,
    get_physical_bottle_by_qr,
    generate_qr_codes_for_bottle,
    remove_physical_bottle,
    move_physical_bottle,
    upload_image,
    get_geocoded_regions,
)
print("ALL IMPORTS OK", flush=True)

print("\n=== BottleBase Schema Check ===", flush=True)
import schemas
b = schemas.BottleBase(name="Test", quantity=5, apogee_start=2020, apogee_end=2030)
print(f"quantity={b.quantity}, apogee_start={b.apogee_start}, apogee_end={b.apogee_end}", flush=True)

print("\n=== Models Relationship Check ===", flush=True)
from models import Bottle, PhysicalBottle, Position
print("Models imported OK", flush=True)

print("\n=== Middleware Check ===", flush=True)
from main import app
print("App loaded OK", flush=True)

print("\nDONE")
