"""Ajout des bouteilles physiques avec QR codes

Revision ID: 003
Revises: 002
Create Date: 2026-04-20 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def _table_exists(connection, table_name):
    result = connection.execute(
        sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name"),
        {"name": table_name}
    ).fetchone()
    return result is not None


def _column_exists(connection, table_name, column_name):
    rows = connection.execute(
        sa.text(f"PRAGMA table_info({table_name})")
    ).fetchall()
    return any(row[1] == column_name for row in rows)


def upgrade():
    connection = op.get_bind()

    # ── 1. Créer la table physical_bottles si absente ──
    if not _table_exists(connection, "physical_bottles"):
        op.create_table(
            "physical_bottles",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("bottle_id", sa.Integer(), sa.ForeignKey("bottles.id"), nullable=False),
            sa.Column("position_id", sa.Integer(), sa.ForeignKey("positions.id"), nullable=True),
            sa.Column("qr_code", sa.String(8), nullable=False),
            sa.Column("status", sa.String(20), nullable=False, server_default="in_cellar"),
            sa.Column("acquisition_date", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("removal_date", sa.DateTime(), nullable=True),
            sa.Column("notes", sa.String(500), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("qr_code"),
        )
        op.create_index("ix_physical_bottles_qr_code", "physical_bottles", ["qr_code"])
        op.create_index("ix_physical_bottles_bottle_id", "physical_bottles", ["bottle_id"])
        op.create_index("ix_physical_bottles_position_id", "physical_bottles", ["position_id"])

    # ── 2. Ajouter la colonne temporaire physical_bottle_id dans positions si absente ──
    # NOTE: cette colonne est temporaire (créée ici, supprimée par 004)
    if not _column_exists(connection, "positions", "physical_bottle_id"):
        op.add_column(
            "positions",
            sa.Column("physical_bottle_id", sa.Integer(), nullable=True)
        )
        op.create_foreign_key(
            "fk_positions_physical_bottle",
            "positions",
            "physical_bottles",
            ["physical_bottle_id"],
            ["id"],
        )

    # ── 3. Migrer les données existantes (si table vient d'être créée) ──
    # Vérifier si des physical_bottles ont été créées SANS données (fresh install)
    count = connection.execute(
        sa.text("SELECT COUNT(*) FROM physical_bottles")
    ).scalar()

    if count == 0:
        # Générer des QR codes pour les bouteilles existantes
        import uuid

        bottles = connection.execute(
            sa.text("""
                SELECT b.id, b.quantity, b.name 
                FROM bottles b 
                WHERE b.quantity > 0
            """)
        ).fetchall()

        for bottle in bottles:
            bottle_id = bottle[0]
            quantity = bottle[1]

            for i in range(quantity):
                qr_code = str(uuid.uuid4())[:8].upper()
                while connection.execute(
                    sa.text("SELECT 1 FROM physical_bottles WHERE qr_code = :qr"),
                    {"qr": qr_code},
                ).fetchone():
                    qr_code = str(uuid.uuid4())[:8].upper()

                result = connection.execute(
                    sa.text("""
                        INSERT INTO physical_bottles (bottle_id, qr_code, status, acquisition_date)
                        VALUES (:bottle_id, :qr_code, 'in_cellar', :acq_date)
                        RETURNING id
                    """),
                    {
                        "bottle_id": bottle_id,
                        "qr_code": qr_code,
                        "acq_date": datetime.utcnow(),
                    },
                )
                physical_bottle_id = result.fetchone()[0]

                position = connection.execute(
                    sa.text("""
                        SELECT p.id 
                        FROM positions p 
                        WHERE p.bottle_id = :bottle_id
                        LIMIT 1 OFFSET :offset
                    """),
                    {"bottle_id": bottle_id, "offset": i},
                ).fetchone()

                if position:
                    position_id = position[0]
                    connection.execute(
                        sa.text("""
                            UPDATE positions 
                            SET physical_bottle_id = :physical_bottle_id
                            WHERE id = :position_id
                        """),
                        {
                            "physical_bottle_id": physical_bottle_id,
                            "position_id": position_id,
                        },
                    )
                    connection.execute(
                        sa.text("""
                            UPDATE physical_bottles 
                            SET position_id = :position_id
                            WHERE id = :physical_bottle_id
                        """),
                        {
                            "position_id": position_id,
                            "physical_bottle_id": physical_bottle_id,
                        },
                    )

    # ── 4. Supprimer la colonne bottle_id de positions (ancienne FK) ──
    # Seulement si elle existe (DB legacy)
    if _column_exists(connection, "positions", "bottle_id"):
        # SQLite-only: reconstruction manuelle
        connection.execute(sa.text("""
            CREATE TABLE positions_new (
                id INTEGER NOT NULL,
                row_id INTEGER NOT NULL,
                line INTEGER NOT NULL,
                position INTEGER NOT NULL,
                physical_bottle_id INTEGER,
                PRIMARY KEY (id),
                FOREIGN KEY(row_id) REFERENCES cave_rows (id),
                FOREIGN KEY(physical_bottle_id) REFERENCES physical_bottles (id)
            )
        """))
        connection.execute(sa.text("""
            INSERT INTO positions_new (id, row_id, line, position, physical_bottle_id)
            SELECT id, row_id, line, position, physical_bottle_id FROM positions
        """))
        connection.execute(sa.text("DROP TABLE positions"))
        connection.execute(sa.text("ALTER TABLE positions_new RENAME TO positions"))


def downgrade():
    op.add_column("positions", sa.Column("bottle_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_positions_bottle", "positions", "bottles", ["bottle_id"], ["id"]
    )

    connection = op.get_bind()
    connection.execute(
        sa.text("""
            UPDATE bottles 
            SET quantity = (
                SELECT COUNT(*) 
                FROM physical_bottles 
                WHERE physical_bottles.bottle_id = bottles.id
            )
        """)
    )

    # SQLite: reconstruction manuelle pour supprimer physical_bottle_id
    connection.execute(sa.text("""
        CREATE TABLE positions_new (
            id INTEGER NOT NULL,
            row_id INTEGER NOT NULL,
            line INTEGER NOT NULL,
            position INTEGER NOT NULL,
            bottle_id INTEGER,
            PRIMARY KEY (id),
            FOREIGN KEY(row_id) REFERENCES cave_rows (id),
            FOREIGN KEY(bottle_id) REFERENCES bottles (id)
        )
    """))
    connection.execute(sa.text("""
        INSERT INTO positions_new (id, row_id, line, position, bottle_id)
        SELECT id, row_id, line, position, bottle_id FROM positions
    """))
    connection.execute(sa.text("DROP TABLE positions"))
    connection.execute(sa.text("ALTER TABLE positions_new RENAME TO positions"))

    op.drop_index("ix_physical_bottles_position_id", "physical_bottles")
    op.drop_index("ix_physical_bottles_bottle_id", "physical_bottles")
    op.drop_index("ix_physical_bottles_qr_code", "physical_bottles")
    op.drop_table("physical_bottles")
