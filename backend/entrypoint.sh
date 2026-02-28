#!/bin/sh
set -e

echo "=== Démarrage de Pinarr ==="

# Créer les répertoires nécessaires
mkdir -p /app/data /app/uploads
chmod 777 /app/data /app/uploads
echo "✓ Répertoires créés"

# Exécuter les migrations Alembic
echo "=== Exécution des migrations ==="
cd /app
alembic upgrade head
echo "✓ Migrations terminées"

# Créer un script Python temporaire pour créer l'admin si nécessaire
cat > /tmp/init_admin.py << 'PYTHON_SCRIPT'
import sys
import os

sys.path.insert(0, '/app')

from database import SessionLocal
from models import User
from auth import hash_password
from sqlalchemy import text

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
        print(f"✓ {user_count} utilisateur(s) existant(s)")
finally:
    db.close()
PYTHON_SCRIPT

python3 /tmp/init_admin.py
rm /tmp/init_admin.py

echo "=== Lancement de l'application ==="
# Lancer l'application
exec uvicorn main:app --host 0.0.0.0 --port 8000
