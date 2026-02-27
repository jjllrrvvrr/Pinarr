#!/bin/sh
set -e

# Créer les répertoires nécessaires AVANT tout
mkdir -p /app/data /app/uploads
chmod 777 /app/data /app/uploads

# Créer un script Python temporaire pour initialiser la DB
cat > /tmp/init_db.py << 'PYTHON_SCRIPT'
import sys
import os

# S'assurer que le répertoire de données existe
os.makedirs('/app/data', exist_ok=True)

sys.path.insert(0, '/app')

# Maintenant importer les modules qui ont besoin de la DB
from database import Base, engine, SessionLocal
from models import User
from auth import hash_password
from sqlalchemy import text

# Créer les tables
Base.metadata.create_all(bind=engine)

# Créer l'admin si pas encore de users
db = SessionLocal()
try:
    # Vérifier si des users existent
    result = db.execute(text("SELECT COUNT(*) FROM users")).fetchone()
    user_count = result[0] if result else 0
    
    if user_count == 0:
        # Créer l'admin
        admin_user = User(
            username=os.getenv("ADMIN_USERNAME", "admin"),
            password_hash=hash_password(os.getenv("ADMIN_PASSWORD", "admin123")),
            is_admin=True
        )
        db.add(admin_user)
        db.commit()
        print(f"✓ Admin créé: {admin_user.username}")
    else:
        print(f"✓ {user_count} utilisateur(s) déjà existant(s)")
finally:
    db.close()
PYTHON_SCRIPT

python3 /tmp/init_db.py
rm /tmp/init_db.py

# Lancer l'application
exec uvicorn main:app --host 0.0.0.0 --port 8000
