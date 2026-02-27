#!/usr/bin/env python3
"""
Script d'initialisation de l'admin Pinarr
Crée l'utilisateur admin si aucun utilisateur n'existe
"""

import os
import sys
import hashlib
import secrets

# Configuration du Python path pour trouver les modules backend
sys.path.insert(0, "/app")
sys.path.insert(0, "/app/backend")

try:
    from database import engine, Base, SessionLocal
    from sqlalchemy import text

    print("✅ Connexion à la base de données réussie")
except Exception as e:
    print(f"❌ Erreur de connexion à la base: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)


def hash_password(password: str) -> str:
    """Hash le mot de passe avec SHA256 + salt (simple mais efficace pour homelab)"""
    salt = secrets.token_hex(16)
    pwdhash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwdhash}"


def init_admin():
    """Crée l'utilisateur admin par défaut"""

    # Variables d'environnement
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_password:
        print("⚠️  ADMIN_PASSWORD non défini, utilisation du mot de passe par défaut")
        admin_password = "admin123"
        print("⚠️  ⚠️  ⚠️  CHANGEZ CE MOT DE PASSE IMMÉDIATEMENT! ⚠️  ⚠️  ⚠️")

    try:
        with SessionLocal() as db:
            # Vérifier si la table users existe
            result = db.execute(
                text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='users'
            """)
            ).fetchone()

            if not result:
                print("📋 Création de la table users...")
                db.execute(
                    text("""
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        is_admin BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                )
                db.commit()
                print("✅ Table users créée")

            # Vérifier si un admin existe déjà
            result = db.execute(
                text("""
                SELECT id FROM users WHERE is_admin = 1 LIMIT 1
            """)
            ).fetchone()

            if result:
                print(f"ℹ️  Un admin existe déjà (ID: {result[0]})")
                return

            # Créer l'admin
            password_hash = hash_password(admin_password)
            db.execute(
                text("""
                INSERT INTO users (username, password_hash, is_admin)
                VALUES (:username, :password_hash, 1)
            """),
                {"username": admin_username, "password_hash": password_hash},
            )
            db.commit()

            print(f"✅ Utilisateur admin créé: {admin_username}")
            print("📝 Connectez-vous avec ces identifiants:")
            print(f"   Username: {admin_username}")
            print(f"   Password: {'*' * len(admin_password)}")

    except Exception as e:
        print(f"❌ Erreur lors de la création de l'admin: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("🔧 Initialisation de Pinarr...")
    print("=" * 50)
    init_admin()
    print("=" * 50)
    print("✨ Prêt!")
