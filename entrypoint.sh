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

# Exécuter les migrations Alembic
echo "Exécution des migrations..."
python3 -m alembic upgrade head || echo "Avertissement: Problème avec les migrations"

# Créer l'utilisateur admin si la base est vide (à la première exécution)
echo "Vérification/Création de l'utilisateur admin..."
python3 << 'PYTHON_SCRIPT'
import sys
import os
sys.path.insert(0, '/app/backend')

try:
    from database import SessionLocal, engine
    from models import User
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    
    # Créer les tables si elles n'existent pas
    from database import Base
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    user_count = session.query(User).count()
    
    admin_user = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_pass = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    if user_count == 0:
        print(f'Création du compte admin par défaut...')
        user = User(
            username=admin_user,
            password_hash=pwd_context.hash(admin_pass),
            is_admin=True
        )
        session.add(user)
        session.commit()
        print(f'✓ Compte admin créé: {admin_user}')
    else:
        print(f'✓ {user_count} utilisateur(s) existant(s)')
    
    session.close()
except Exception as e:
    print(f'⚠ Erreur lors de la création admin: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(0)  # Ne pas bloquer le démarrage
PYTHON_SCRIPT

# Démarrer le backend en arrière-plan
echo "Démarrage du backend..."
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &

# Attendre que le backend soit prêt
echo "Attente du backend..."
sleep 3

# Démarrer Nginx au premier plan
echo "Démarrage de Nginx..."
nginx -g 'daemon off;'
