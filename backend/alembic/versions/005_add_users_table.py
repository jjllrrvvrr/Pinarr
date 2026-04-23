"""Ajout de la table users

Revision ID: 005
Revises: 004
Create Date: 2026-04-23 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def _table_exists(connection, table_name):
    result = connection.execute(
        sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name"),
        {"name": table_name}
    ).fetchone()
    return result is not None


def upgrade():
    connection = op.get_bind()

    if not _table_exists(connection, "users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("username", sa.String(), nullable=False),
            sa.Column("password_hash", sa.String(), nullable=False),
            sa.Column("is_admin", sa.Boolean(), default=True),
            sa.Column("created_at", sa.DateTime(), default=sa.func.now()),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("username"),
        )
        op.create_index("ix_users_username", "users", ["username"])


def downgrade():
    op.drop_index("ix_users_username", "users")
    op.drop_table("users")
