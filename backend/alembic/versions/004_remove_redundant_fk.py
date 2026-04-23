"""Suppression de physical_bottle_id dans positions (reconstruction SQLite)

SQLite ne supporte pas ALTER TABLE DROP COLUMN avec
une contrainte FK qui y fait référence.
On reconstruit la table manuellement à la place.

Revision ID: 004
Revises: 003
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def _has_col(connection, table, col):
    rows = connection.execute(sa.text(f"PRAGMA table_info({table})")).fetchall()
    return any(r[1] == col for r in rows)


def _has_table(connection, table):
    rows = connection.execute(
        sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name=:t"),
        {"t": table}
    ).fetchall()
    return bool(rows)


def upgrade():
    connection = op.get_bind()

    # Rien à faire si la table n'existe pas encore (create_db_tables)
    if not _has_table(connection, "positions"):
        return

    # Rien à faire si la colonne est déjà absente
    if not _has_col(connection, "positions", "physical_bottle_id"):
        return

    # Reconstruction manuelle car SQLite n'aime pas DROP COLUMN + FK
    # 1. Créer la nouvelle table sans physical_bottle_id
    connection.execute(
        sa.text("""
            CREATE TABLE positions_new (
                id INTEGER NOT NULL,
                row_id INTEGER NOT NULL,
                line INTEGER NOT NULL,
                position INTEGER NOT NULL,
                PRIMARY KEY (id),
                FOREIGN KEY (row_id) REFERENCES cave_rows (id)
            )
        """)
    )

    # 2. Copier les données
    connection.execute(
        sa.text("INSERT INTO positions_new (id, row_id, line, position) SELECT id, row_id, line, position FROM positions")
    )

    # 3. Supprimer l'ancienne
    connection.execute(sa.text("DROP TABLE positions"))

    # 4. Renommer
    connection.execute(sa.text("ALTER TABLE positions_new RENAME TO positions"))


def downgrade():
    op.add_column(
        "positions", sa.Column("physical_bottle_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        "fk_positions_physical_bottle",
        "positions",
        "physical_bottles",
        ["physical_bottle_id"],
        ["id"],
    )
