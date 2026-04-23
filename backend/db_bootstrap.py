#!/usr/bin/env python3
"""Bootstrap de la base de données pour Pinarr.

Ce script est le seul point d'entrée pour la gestion du schéma.
Il détecte l'état de la DB et agit en conséquence :
- DB vide          → crée les tables via SQLAlchemy, puis stamp Alembic HEAD
- DB legacy        → détecte le schéma, stamp Alembic, puis upgrade head
- DB versionnée    → alembic upgrade head classique
"""

import os
import sqlite3
import subprocess
import sys

HEAD = "005"


def _resolve_db_path() -> str:
    """Miroite exactement la logique de database.py."""
    database_url = os.getenv("DATABASE_URL", "sqlite:///./pinarr.db")
    if database_url.startswith("sqlite:///./"):
        db_file = database_url[12:]  # après "sqlite:///./"
        if db_file.startswith("data/"):
            db_file = db_file[5:]
        return f"sqlite:////app/data/{db_file}".replace("sqlite://", "")
    return database_url.replace("sqlite://", "")


def _db_exists(db_path: str) -> bool:
    conn = sqlite3.connect(db_path)
    try:
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return len(c.fetchall()) > 0
    finally:
        conn.close()


def _detect_schema_state(conn: sqlite3.Connection) -> str:
    """Détecte l'état du schéma.
    Retours : fresh, 002, 003, 004, 005, unknown
    """
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in c.fetchall()}

    if not tables:
        return "fresh"

    if "alembic_version" in tables:
        c.execute("SELECT version_num FROM alembic_version")
        row = c.fetchone()
        if row and row[0]:
            return row[0]

    # Legacy detection (no alembic_version table)
    if "bottles" not in tables:
        return "unknown"

    c.execute("PRAGMA table_info(bottles)")
    cols = {col[1] for col in c.fetchall()}

    if "jeunesse_end" not in cols:
        return "unknown"  # Pré-002 non supporté

    if "physical_bottles" not in tables:
        return "002"

    # physical_bottles existe : différencier 003 / 004 / 005
    if "users" in tables:
        return "005"

    c.execute("PRAGMA table_info(positions)")
    pos_cols = {col[1] for col in c.fetchall()}
    return "003" if "physical_bottle_id" in pos_cols else "004"


def _stamp(version: str) -> None:
    print(f"[DB]   Stamp Alembic —> {version}")
    subprocess.run(["python3", "-m", "alembic", "stamp", version], check=True)


def _upgrade_head() -> None:
    print("[DB]   Alembic upgrade head")
    subprocess.run(["python3", "-m", "alembic", "upgrade", "head"], check=True)


def _create_tables() -> None:
    print("[DB]   Création tables fraîches")
    sys.path.insert(0, "/app/backend")
    from database import create_db_tables
    create_db_tables()


def bootstrap():
    db_path = _resolve_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    print(f"[DB]   Path: {db_path}")

    if not _db_exists(db_path):
        _create_tables()
        _stamp(HEAD)
        print("[DB]   ✅ DB initiale prête.")
        return

    conn = sqlite3.connect(db_path)
    try:
        state = _detect_schema_state(conn)
    finally:
        conn.close()
    print(f"[DB]   State: {state}")

    if state == HEAD:
        _upgrade_head()
        print("[DB]   ✅ À jour.")
    elif state in ("002", "003", "004"):
        _stamp(state)
        _upgrade_head()
        print("[DB]   ✅ Upgrade terminé.")
    else:
        # unknown ou version inconnue : tentative upgrade
        print(f"[DB]   WARN state={state}, tentative upgrade head")
        _upgrade_head()
        print("[DB]   ✅ Tentative terminée.")


if __name__ == "__main__":
    bootstrap()
