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

# S'assurer que les répertoires de données existent
mkdir -p /app/data /app/uploads

# Se déplacer dans le répertoire backend
cd /app/backend

# Exécuter les migrations Alembic
python3 -m alembic upgrade head || echo "Aucune migration nécessaire ou erreur ignorée"

# Créer l'utilisateur admin si la base est vide (à la première exécution)
python3 -c "
import sys
sys.path.insert(0, '/app/backend')
from database import SessionLocal
from models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

session = SessionLocal()
user_count = session.query(User).count()
if user_count == 0:
    print('Création du compte admin par défaut...')
    user = User(
        username='$ADMIN_USERNAME',
        password_hash=pwd_context.hash('$ADMIN_PASSWORD'),
        is_admin=True
    )
    session.add(user)
    session.commit()
    print(f'Compte admin créé: $ADMIN_USERNAME')
session.close()
" 2>/dev/null || echo "Ignorer la création auto de l'admin"

# Démarrer le backend en arrière-plan
echo "Démarrage du backend..."
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &

# Attendre que le backend soit prêt
echo "Attente du backend..."
sleep 3

# Démarrer Nginx au premier plan
echo "Démarrage de Nginx..."
nginx -g 'daemon off;'
