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
)

from .upload_service import upload_image, delete_image

from .geo_service import get_geocoded_regions, create_geocoded_region

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
    "upload_image",
    "delete_image",
    "get_geocoded_regions",
    "create_geocoded_region",
]
