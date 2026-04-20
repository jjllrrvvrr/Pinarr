"""Ajout des bouteilles physiques avec QR codes

Revision ID: 003
Revises: 002
Create Date: 2026-04-20 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import String, Integer, DateTime, ForeignKey
from datetime import datetime
import uuid


# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def generate_qr_code():
    """Génère un code QR unique de 8 caractères alphanumériques."""
    return str(uuid.uuid4())[:8].upper()


def upgrade() -> None:
    # ### Créer la table physical_bottles ###
    op.create_table(
        "physical_bottles",
        sa.Column("id", Integer(), nullable=False),
        sa.Column("bottle_id", Integer(), ForeignKey("bottles.id"), nullable=False),
        sa.Column("position_id", Integer(), ForeignKey("positions.id"), nullable=True),
        sa.Column("qr_code", String(8), nullable=False),
        sa.Column("status", String(20), nullable=False, server_default="in_cellar"),
        sa.Column(
            "acquisition_date", DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("removal_date", DateTime(), nullable=True),
        sa.Column("notes", String(500), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("qr_code"),
    )
    op.create_index("ix_physical_bottles_qr_code", "physical_bottles", ["qr_code"])
    op.create_index("ix_physical_bottles_bottle_id", "physical_bottles", ["bottle_id"])
    op.create_index(
        "ix_physical_bottles_position_id", "physical_bottles", ["position_id"]
    )

    # ### Créer une colonne temporaire dans positions pour physical_bottle_id ###
    op.add_column(
        "positions", sa.Column("physical_bottle_id", Integer(), nullable=True)
    )
    op.create_foreign_key(
        "fk_positions_physical_bottle",
        "positions",
        "physical_bottles",
        ["physical_bottle_id"],
        ["id"],
    )

    # ### Migrer les données existantes ###
    connection = op.get_bind()

    # Récupérer toutes les bouteilles avec leur quantity et positions
    bottles = connection.execute(
        sa.text("""
            SELECT b.id, b.quantity, b.name 
            FROM bottles b 
            WHERE b.quantity > 0
        """)
    ).fetchall()

    # Pour chaque bouteille, créer les physical_bottles
    for bottle in bottles:
        bottle_id = bottle[0]
        quantity = bottle[1]

        # Créer N physical_bottles (N = quantity)
        for i in range(quantity):
            qr_code = generate_qr_code()

            # Vérifier que le code n'existe pas déjà
            while connection.execute(
                sa.text("SELECT 1 FROM physical_bottles WHERE qr_code = :qr"),
                {"qr": qr_code},
            ).fetchone():
                qr_code = generate_qr_code()

            # Insérer la physical_bottle
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

            # Mettre à jour la position existante (si elle existe)
            # On prend la première position libre ou déjà assignée à cette bouteille
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

                # Mettre à jour la physical_bottle avec sa position
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

    # ### Supprimer la colonne bottle_id de positions ###
    op.drop_constraint("fk_positions_bottle", "positions", type_="foreignkey")
    op.drop_column("positions", "bottle_id")


def downgrade() -> None:
    # ### Remettre la colonne bottle_id dans positions ###
    op.add_column("positions", sa.Column("bottle_id", Integer(), nullable=True))
    op.create_foreign_key(
        "fk_positions_bottle", "positions", "bottles", ["bottle_id"], ["id"]
    )

    # ### Restaurer les quantities dans bottles ###
    connection = op.get_bind()

    # Compter les physical_bottles par bottle et mettre à jour quantity
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

    # Réassigner les positions aux bottles (simplifié - prend le premier physical_bottle)
    connection.execute(
        sa.text("""
            UPDATE positions p
            SET bottle_id = pb.bottle_id
            FROM physical_bottles pb
            WHERE p.physical_bottle_id = pb.id
        """)
    )

    # ### Supprimer la colonne physical_bottle_id de positions ###
    op.drop_constraint("fk_positions_physical_bottle", "positions", type_="foreignkey")
    op.drop_column("positions", "physical_bottle_id")

    # ### Supprimer la table physical_bottles ###
    op.drop_index("ix_physical_bottles_position_id", "physical_bottles")
    op.drop_index("ix_physical_bottles_bottle_id", "physical_bottles")
    op.drop_index("ix_physical_bottles_qr_code", "physical_bottles")
    op.drop_table("physical_bottles")
