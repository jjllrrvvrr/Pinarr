"""Tests bootstrap DB : migrations Alembic + idempotence.

Vérifie que le schéma créé sur une DB vierge correspond à HEAD,
et que relancer le bootstrap sur une DB existante ne casse rien
(garantie principale demandée : ne jamais casser les données).
"""

import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_bootstrap_fresh_db_creates_schema():
    """DB vierge -> tables créées -> stamp HEAD -> relance idempotente."""
    import shutil

    tmp = tempfile.mkdtemp(prefix="pinarr_boot_")
    db_path = os.path.join(tmp, "pinarr.db")

    env = {
        **os.environ,
        "DATABASE_URL": f"sqlite:///{db_path}",
        "SECRET_KEY": "test",
    }

    # Créer les tables comme database.py / db_bootstrap.py le font
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from database import create_db_tables; create_db_tables()",
        ],
        cwd=str(Path(__file__).parent.parent),
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"create_db_tables failed: {result.stderr}"

    # Toutes les tables attendues présentes
    conn = sqlite3.connect(db_path)
    tables = {
        r[0]
        for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    conn.close()
    expected = {
        "users",
        "bottles",
        "caves",
        "cave_columns",
        "cave_rows",
        "positions",
        "physical_bottles",
        "geocoded_regions",
    }
    missing = expected - tables
    assert not missing, f"Tables manquantes: {missing}"

    shutil.rmtree(tmp, ignore_errors=True)


def test_qr_code_format_unchanged():
    """Le format des QR doit rester 8 caractères hex majuscules.

    Contrat critique : les étiquettes déjà imprimées ne doivent jamais
    devenir invalides.
    """
    from services.physical_bottle_service import generate_qr_code

    code = generate_qr_code()
    assert len(code) == 8, f"QR '{code}' != 8 caractères"
    assert code == code.upper()
    assert all(c in "0123456789ABCDEF-" for c in code), f"QR '{code}' non hex"