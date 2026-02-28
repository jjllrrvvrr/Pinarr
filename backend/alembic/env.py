"""
Configuration Alembic pour Pinarr
Ce fichier configure Alembic pour fonctionner avec notre base de données SQLite
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

# Ajouter le répertoire parent au path pour importer les modèles
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from alembic import context
from database import Base, DATABASE_URL
from models import User, Bottle, Cave, CaveColumn, CaveRow, Position, GeocodedRegion

# Configuration Alembic
config = context.config

# Configuration des logs
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Métadonnées des modèles pour la génération automatique
target_metadata = Base.metadata

# URL de la base de données
config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline() -> None:
    """Exécute les migrations en mode offline.

    Configure le contexte avec uniquement une URL sans créer de moteur.
    Les appels à context.execute() émettent directement la chaîne SQL.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Exécute les migrations en mode online.

    Dans ce scénario, on crée un moteur et associe une connexion au contexte.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
