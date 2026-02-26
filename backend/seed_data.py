import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, create_db_tables
from models import Base, Cave, CaveColumn, CaveRow, Position, Bottle


def seed_database():
    create_db_tables()
    db = SessionLocal()

    try:
        if db.query(Cave).count() > 0:
            print("Database already seeded")
            return

        print("Seeding database...")

        cave = Cave(name="Ma Cave")
        db.add(cave)
        db.flush()

        col_a = CaveColumn(cave_id=cave.id, name="Colonne A", order=1)
        col_b = CaveColumn(cave_id=cave.id, name="Colonne B", order=2)
        col_c = CaveColumn(cave_id=cave.id, name="Colonne C", order=3)
        db.add_all([col_a, col_b, col_c])
        db.flush()

        row_a1 = CaveRow(
            column_id=col_a.id, name="Étagère A1", width=6, height=3, order=1
        )
        row_a2 = CaveRow(
            column_id=col_a.id, name="Étagère A2", width=6, height=3, order=2
        )
        row_b1 = CaveRow(
            column_id=col_b.id, name="Étagère B1", width=8, height=4, order=1
        )
        row_b2 = CaveRow(
            column_id=col_b.id, name="Étagère B2", width=8, height=4, order=2
        )
        row_c1 = CaveRow(
            column_id=col_c.id, name="Étagère C1", width=4, height=2, order=1
        )
        db.add_all([row_a1, row_a2, row_b1, row_b2, row_c1])
        db.flush()

        bottles = [
            Bottle(
                name="Château Margaux 2015",
                domaine="Château Margaux",
                year=2015,
                type="Rouge",
                region="Bordeaux",
                cepage="Cabernet Sauvignon, Merlot",
                alcohol=13.5,
                quantity=8,
                price=45.5,
                description="Un vin exceptionnel avec des notes de cassis et de vanille.",
                rating=5,
                size="75cl",
                apogee_start=2020,
                apogee_end=2035,
            ),
            Bottle(
                name="Pouilly-Fumé 2020",
                domaine="Domaine Serge Dagueneau",
                year=2020,
                type="Blanc",
                region="Loire",
                cepage="Sauvignon Blanc",
                alcohol=12.5,
                quantity=10,
                price=18.9,
                description="Un sauvignon frais et minéral.",
                rating=4,
                size="75cl",
                apogee_start=2022,
                apogee_end=2025,
            ),
            Bottle(
                name="Champagne Bollinger",
                domaine="Bollinger",
                year=2018,
                type="Champagne",
                region="Champagne",
                cepage="Pinot Noir, Chardonnay",
                alcohol=12.0,
                quantity=6,
                price=42.0,
                description="Un champagne d'exception.",
                rating=5,
                size="75cl",
                apogee_start=2020,
                apogee_end=2023,
            ),
            Bottle(
                name="Rosé de Provence",
                domaine="Domaine de la Tortinière",
                year=2023,
                type="Rosé",
                region="Provence",
                cepage="Grenache, Cinsault",
                alcohol=13.0,
                quantity=7,
                price=12.5,
                description="Un rosé frais et fruité.",
                rating=3,
                size="75cl",
                apogee_start=2024,
                apogee_end=2025,
            ),
            Bottle(
                name="Saint-Émilion",
                domaine="Château Fombrauge",
                year=2018,
                type="Rouge",
                region="Bordeaux",
                cepage="Merlot, Cabernet Franc",
                alcohol=14.0,
                quantity=5,
                price=35.0,
                description="Un vin complexe et élégant.",
                rating=4,
                size="75cl",
                apogee_start=2022,
                apogee_end=2030,
            ),
        ]
        db.add_all(bottles)
        db.flush()

        pos_a1_1 = Position(
            row_id=row_a1.id, line=1, position=1, bottle_id=bottles[0].id
        )
        pos_a1_2 = Position(
            row_id=row_a1.id, line=1, position=2, bottle_id=bottles[0].id
        )
        pos_a1_3 = Position(
            row_id=row_a1.id, line=1, position=3, bottle_id=bottles[1].id
        )
        pos_a1_4 = Position(
            row_id=row_a1.id, line=1, position=4, bottle_id=bottles[2].id
        )
        pos_a2_1 = Position(
            row_id=row_a2.id, line=2, position=1, bottle_id=bottles[3].id
        )
        pos_a2_2 = Position(
            row_id=row_a2.id, line=2, position=2, bottle_id=bottles[4].id
        )
        pos_b1_1 = Position(
            row_id=row_b1.id, line=1, position=1, bottle_id=bottles[0].id
        )
        pos_b1_2 = Position(
            row_id=row_b1.id, line=1, position=2, bottle_id=bottles[1].id
        )
        pos_b1_3 = Position(
            row_id=row_b1.id, line=1, position=3, bottle_id=bottles[2].id
        )
        pos_c1_1 = Position(
            row_id=row_c1.id, line=1, position=1, bottle_id=bottles[3].id
        )
        pos_c1_2 = Position(
            row_id=row_c1.id, line=1, position=2, bottle_id=bottles[4].id
        )
        db.add_all(
            [
                pos_a1_1,
                pos_a1_2,
                pos_a1_3,
                pos_a1_4,
                pos_a2_1,
                pos_a2_2,
                pos_b1_1,
                pos_b1_2,
                pos_b1_3,
                pos_c1_1,
                pos_c1_2,
            ]
        )

        db.commit()
        print("Database seeded successfully!")
        print(f"  - 1 cave with 3 columns")
        print(f"  - 5 rows with positions")
        print(f"  - 5 wines")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
