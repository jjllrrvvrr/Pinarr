#!/bin/sh
set -e

# Générer un SECRET_KEY aléatoire si non défini
if [ -z "$SECRET_KEY" ]; then
    export SECRET_KEY=$(openssl rand -hex 32)
    echo "SECRET_KEY généré automatiquement"
fi

# Définir les valeurs par défaut pour admin
export ADMIN_USERNAME=${ADMIN_USERNAME:-admin}
export ADMIN_PASSWORD=${ADMIN_PASSWORD:-admin123}

echo "Configuration: ADMIN_USERNAME=$ADMIN_USERNAME"

# S'assurer que les répertoires de données existent
mkdir -p /app/data /app/uploads

# Se déplacer dans le répertoire backend
cd /app/backend

# ── Bootstrap de la base de données ──
# Ce script détecte l'état de la DB et agit en conséquence :
# - DB vide       → crée les tables via SQLAlchemy, puis stamp Alembic
# - DB legacy     → détecte le schéma, stamp Alembic, puis upgrade head
# - DB versionnée → alembic upgrade head classique (idempotent)
echo "=== DB Bootstrap ==="
python3 /app/backend/db_bootstrap.py
echo "✓ DB bootstrap terminé"

# ── Vérification/Création de l'utilisateur admin ──
echo "Vérification/Création de l'utilisateur admin..."
python3 << 'PYTHON_SCRIPT'
import sys, os
sys.path.insert(0, '/app/backend')

try:
    import bcrypt
    from database import SessionLocal
    from models import User
    
    def hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    session = SessionLocal()
    user_count = session.query(User).count()
    
    if user_count == 0:
        admin_user = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_pass = os.environ.get('ADMIN_PASSWORD', 'admin123')[:72]
        user = User(
            username=admin_user,
            password_hash=hash_password(admin_pass),
            is_admin=True
        )
        session.add(user)
        session.commit()
        print(f'✓ Compte admin créé: {admin_user}')
    else:
        print(f'✓ {user_count} utilisateur(s) existant(s)')
    
    session.close()
except Exception as e:
    print(f'⚠ Erreur admin: {e}')
    import traceback
    traceback.print_exc()
    # Ne PAS bloquer le démarrage si l'admin existe déjà
PYTHON_SCRIPT

# ── Démarrage applications ──
echo "Démarrage du backend..."
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &

echo "Attente du backend..."
sleep 3

echo "Démarrage de Nginx..."
nginx -g 'daemon off;'
