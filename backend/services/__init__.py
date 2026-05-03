"""Services pour Pinarr."""

from .bottle_service import (
    get_bottles_with_positions,
    get_bottle_with_position,
    check_duplicate_bottles,
    create_bottle,
    update_bottle,
    patch_bottle,
    delete_bottle,
    validate_bottle_placement,
)

from .cave_service import (
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
    assign_bottle_to_position,
    remove_bottle_from_position,
    consume_bottle_from_position,
)

from .physical_bottle_service import (
    get_physical_bottle_by_qr,
    get_physical_bottle_with_details,
    get_bottle_physical_bottles,
    generate_qr_codes_for_bottle,
    remove_physical_bottle,
    move_physical_bottle,
    get_physical_bottle_count_in_cellar,
)

from .upload_service import upload_image, delete_image, upload_image_from_url

from .geo_service import get_geocoded_regions, create_geocoded_region
from .label_service import generate_label_zip, generate_single_label_pdf

__all__ = [
    "get_bottles_with_positions",
    "get_bottle_with_position",
    "check_duplicate_bottles",
    "create_bottle",
    "update_bottle",
    "patch_bottle",
    "delete_bottle",
    "validate_bottle_placement",
    "get_caves",
    "get_cave",
    "create_cave",
    "update_cave",
    "delete_cave",
    "create_column",
    "update_column",
    "delete_column",
    "create_row",
    "update_row",
    "delete_row",
    "get_positions_for_row",
    "create_position",
    "get_or_create_position",
    "assign_bottle_to_position",
    "remove_bottle_from_position",
    "consume_bottle_from_position",
    "get_physical_bottle_by_qr",
    "get_physical_bottle_with_details",
    "get_bottle_physical_bottles",
    "generate_qr_codes_for_bottle",
    "remove_physical_bottle",
    "move_physical_bottle",
    "get_physical_bottle_count_in_cellar",
    "upload_image",
    "delete_image",
    "upload_image_from_url",
    "get_geocoded_regions",
    "create_geocoded_region",
    "generate_label_zip",
]
