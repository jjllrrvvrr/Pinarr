# Pinarr 🍷

Application de gestion de cave à vin self-hosted avec Docker.

## Fonctionnalités

- 📊 **Gestion complète** : Bouteilles, caves, positions
- 🗺️ **Cartographie** : Visualisation géographique des régions viticoles
- 🔐 **Authentification sécurisée** : Session-based avec tokens JWT
- 📱 **Responsive** : Interface web moderne (Vue.js 3)
- 💾 **Backups automatiques** : SQLite avec rotation quotidienne
- 🐳 **Docker-ready** : Déploiement en 2 commandes

## Architecture

```
Pinarr/
├── backend/           # API FastAPI (Python)
│   ├── models.py      # Modèles SQLAlchemy
│   ├── auth.py        # Authentification JWT
│   └── routers/       # Routes API
├── frontend/          # Vue.js 3 + Tailwind
│   └── src/
│       ├── views/     # Composants Vue
│       └── services/  # Services JS
├── docker-compose.yml # Configuration Docker
├── .env.example       # Template configuration
└── scripts/           # Scripts utilitaires
```

## Déploiement Docker 🚀

### Prérequis

- Docker 20.10+
- Docker Compose 2.0+
- 512 Mo RAM minimum
- 1 Go d'espace disque

### Installation rapide

**1. Cloner le projet**

```bash
git clone <url-du-projet>
cd sudowine
```

**2. Configuration**

```bash
# Copier le template de configuration
cp .env.example .env

# Éditer le fichier .env avec vos paramètres
nano .env
```

**Paramètres importants dans `.env`** :

```bash
# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=votre_mot_de_passe_secure    # ⚠️ CHANGEZ CECI !

# Sécurité
SECRET_KEY=cle_aleatoire_32_caracteres      # Générer avec: openssl rand -hex 32

# Réseau
DOMAIN=http://192.168.1.100                 # Votre IP locale
FRONTEND_PORT=80                            # Port d'accès web
BACKEND_PORT=8000                           # Port API (interne)
```

**3. Lancer l'application**

```bash
# Premier lancement (build les images)
docker-compose up --build -d

# Ou si les images sont déjà buildées
docker-compose up -d
```

**4. Accéder à l'application**

- Web : `http://<VOTRE_IP>:80` ou `http://<VOTRE_IP>`
- API : `http://<VOTRE_IP>:8000`

Par défaut :
- **Username** : `admin` (ou celui défini dans .env)
- **Password** : Celui défini dans `ADMIN_PASSWORD`

### Commandes utiles

```bash
# Voir les logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Redémarrer un service
docker-compose restart backend
docker-compose restart frontend

# Mettre à jour
docker-compose pull
docker-compose up -d

# Arrêter
docker-compose down

# Backup manuel
docker-compose exec backend python scripts/backup-db.sh
```

## Sécurité 🔐

### Mot de passe

Par défaut, l'application crée un utilisateur admin au premier démarrage. **Changez immédiatement le mot de passe par défaut** :

1. Connectez-vous avec les identifiants par défaut
2. Allez dans les paramètres
3. Changez le mot de passe

### Bonnes pratiques

- ✅ Utilisez un mot de passe fort (12+ caractères)
- ✅ Changez la `SECRET_KEY` (générez avec `openssl rand -hex 32`)
- ✅ Gardez votre `.env` secret (non versionné)
- ✅ Activez le firewall sur votre serveur
- ✅ Faites des backups réguliers

## Configuration avancée

### Production (optimisé)

```bash
# Utiliser docker-compose.prod.yml pour les optimisations
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Ce fichier ajoute :
- Limites de ressources (CPU/RAM)
- Rotation des logs
- Backup automatique quotidien (2h du matin)

### Backup automatique

Les backups sont créés automatiquement dans `./backup/` :
- 1 backup/jour conservé 30 jours
- Format : `sudowine_backup_YYYYMMDD_HHMMSS.db.gz`

**Restaurer un backup** :

```bash
# Arrêter l'application
docker-compose down

# Extraire le backup
gunzip backup/sudowine_backup_20240115_020000.db.gz

# Remplacer la base
cp backup/sudowine_backup_20240115_020000.db backend/data/sudo_wine.db

# Redémarrer
docker-compose up -d
```

### Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|---------|
| `ADMIN_USERNAME` | Nom admin | `admin` |
| `ADMIN_PASSWORD` | Mot de passe | **obligatoire** |
| `SECRET_KEY` | Clé JWT | **changer** |
| `DOMAIN` | URL d'accès | `http://localhost` |
| `SESSION_EXPIRE_HOURS` | Durée session | `24` |
| `BACKUP_RETENTION_DAYS` | Jours de retention | `30` |

## Dépannage

### L'application ne démarre pas

```bash
# Vérifier les logs
docker-compose logs

# Vérifier les ports
docker-compose ps
```

### Erreur "Identifiants invalides"

- Vérifiez les variables `ADMIN_USERNAME` et `ADMIN_PASSWORD` dans `.env`
- Redémarrez avec `docker-compose restart backend`

### Base de données corrompue

```bash
# Restaurer depuis le dernier backup
docker-compose down
cd backup
LATEST=$(ls -t *.db.gz | head -1)
gunzip "$LATEST"
cp "${LATEST%.gz}" ../backend/data/sudo_wine.db
cd ..
docker-compose up -d
```

### Problèmes de permissions

```bash
# Fixer les permissions
docker-compose down
sudo chown -R $USER:$USER .
docker-compose up -d
```

## Développement

### Structure du projet

```
sudowine/
├── backend/           # FastAPI
│   ├── main.py        # Entry point
│   ├── models.py      # Database models
│   ├── auth.py        # Authentication
│   └── services/      # Business logic
├── frontend/          # Vue.js
│   └── src/
│       ├── views/     # Pages
│       ├── components/# UI components
│       └── services/  # API calls
├── scripts/           # Utils
│   ├── init-admin.py  # Create admin user
│   └── backup-db.sh   # Backup script
└── docker-compose.yml # Docker config
```

### Développement local

**Backend** :
```bash
cd backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend** :
```bash
cd frontend
npm install
npm run dev
```

## Licence

MIT License - Libre d'utilisation pour usage personnel et commercial.

## Support

- 🐛 Issues : [GitHub Issues](https://github.com/votre-repo/sudowine/issues)
- 📧 Email : votre-email@example.com
- 💬 Discord : [Votre serveur]

---

**Made with ❤️ for wine lovers** 🍷
