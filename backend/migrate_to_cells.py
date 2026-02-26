#!/usr/bin/env python3
"""
Migration script: Convert old shelf_position system to new Cell/CellBottle system

This script:
1. Creates Cell and CellBottle tables (if not exists)
2. Migrates existing bottles with shelf_position to CellBottle records
3. Creates cells for existing shelves
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    MetaData,
    Table,
    text,
)
from sqlalchemy.orm import sessionmaker
from database import SQLALCHEMY_DATABASE_URL, SessionLocal


def migrate():
    print("Starting migration to Cell-based system...")

    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Check if Cell table exists
        inspector = MetaData()
        inspector.reflect(bind=engine)

        if "cells" in inspector.tables:
            print("Cell table already exists, skipping migration")
            return

        print("Creating new tables...")

        # Create Cell table
        cells_table = Table(
            "cells",
            inspector,
            Column("id", String, primary_key=True),
            Column("shelf_id", Integer, ForeignKey("shelves.id"), nullable=False),
            Column("row", Integer, nullable=False),
            Column("col", Integer, nullable=False),
            Column("max_capacity", Integer, nullable=True),
        )
        cells_table.create(engine)

        # Create CellBottle table
        cell_bottles_table = Table(
            "cell_bottles",
            inspector,
            Column("cell_id", String, ForeignKey("cells.id"), primary_key=True),
            Column("bottle_id", Integer, ForeignKey("bottles.id"), primary_key=True),
            Column("quantity", Integer, nullable=False, default=1),
        )
        cell_bottles_table.create(engine)

        # Add type column to shelves if not exists
        if "type" not in [c.name for c in inspector.tables["shelves"].columns]:
            print("Adding 'type' column to shelves...")
            session.execute(
                text("ALTER TABLE shelves ADD COLUMN type VARCHAR DEFAULT 'grid'")
            )
            session.commit()

        print("Migrating existing bottles...")

        # Get all bottles with shelf_position
        result = session.execute(
            text(
                "SELECT id, shelf_id, shelf_position, quantity FROM bottles WHERE shelf_id IS NOT NULL"
            )
        )

        bottles_with_position = result.fetchall()
        print(f"Found {len(bottles_with_position)} bottles to migrate")

        for bottle_id, shelf_id, shelf_position, quantity in bottles_with_position:
            if not shelf_position:
                continue

            # Parse position (format: "row,col")
            try:
                parts = shelf_position.split(",")
                row = int(parts[0])
                col = int(parts[1])
            except (ValueError, IndexError):
                print(
                    f"  Warning: Invalid position '{shelf_position}' for bottle {bottle_id}, skipping"
                )
                continue

            # Generate cell ID
            cell_id = f"shelf_{shelf_id}_{row}_{col}"

            # Check if cell exists, create if not
            existing_cell = session.execute(
                text("SELECT id FROM cells WHERE id = :cell_id"), {"cell_id": cell_id}
            ).fetchone()

            if not existing_cell:
                # Create cell
                session.execute(
                    text(
                        "INSERT INTO cells (id, shelf_id, row, col) VALUES (:id, :shelf_id, :row, :col)"
                    ),
                    {"id": cell_id, "shelf_id": shelf_id, "row": row, "col": col},
                )

            # Create CellBottle association
            session.execute(
                text(
                    "INSERT INTO cell_bottles (cell_id, bottle_id, quantity) VALUES (:cell_id, :bottle_id, :quantity)"
                ),
                {"cell_id": cell_id, "bottle_id": bottle_id, "quantity": quantity},
            )

            print(f"  Migrated bottle {bottle_id} to cell {cell_id}")

        session.commit()
        print("\nMigration completed successfully!")

        # Note: We keep shelf_id and shelf_position columns for now
        # They can be removed in a future migration after everything is verified

    except Exception as e:
        session.rollback()
        print(f"Error during migration: {e}")
        raise
    finally:
        session.close()
        engine.dispose()


if __name__ == "__main__":
    migrate()
