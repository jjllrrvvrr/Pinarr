# Pinarr 🍷

Application de gestion de cave à vin self-hosted avec Docker.

## Fonctionnalités

- 📊 **Gestion complète** : Bouteilles, caves, positions
- 🗺️ **Cartographie** : Visualisation géographique des régions viticoles
- 🔐 **Authentification sécurisée** : Session-based avec tokens JWT
- 🖼️ **Gestion des images** : Upload de photos de bouteilles
- 🔄 **Migrations automatiques** : Mises à jour sans perte de données
- 📱 **Responsive** : Interface web moderne (Vue.js 3)
- 🐳 **Docker-ready** : Déploiement en 2 commandes

## Installation Docker

### Prérequis

- Docker 20.10+
- Docker Compose 2.0+
- 512 Mo RAM minimum
- 1 Go d'espace disque

### Déploiement rapide

**1. Cloner le projet**

```bash
git clone https://github.com/jjllrrvvrr/Pinarr.git
cd Pinarr
```

**2. Configurer**

Modifiez le fichier `.env` avec vos paramètres :

```bash
# Éditer le fichier .env
nano .env
```

**Variables obligatoires à modifier :**

```bash
# IP de votre serveur (obligatoire!)
# Trouvez votre IP avec:
#   - Mac/Linux: ifconfig ou ip addr
#   - Windows: ipconfig
HOST_IP=192.168.1.100

# Changez le mot de passe admin par défaut!
ADMIN_PASSWORD=votre_mot_de_passe_securise
```

**Variables optionnelles :**

```bash
# Ports (défaut: 8908 pour frontend, 9994 pour backend)
FRONTEND_PORT=8908
BACKEND_PORT=9994

# Identifiants admin
ADMIN_USERNAME=admin

# Clé secrète JWT (générée auto si vide)
SECRET_KEY=
```

**3. Lancer**

```bash
docker-compose up -d
```

**4. Accéder**

- Application : `http://votre-ip:8908`
- Login par défaut : `admin` / (mot de passe défini dans `.env`)

### Mise à jour

Pour mettre à jour vers la dernière version :

```bash
# 1. Récupérer les dernières modifications
git pull

# 2. Rebuild et redémarrer (les données sont préservées)
docker-compose down
docker-compose up -d --build
```

✅ **Vos données sont automatiquement préservées** lors des mises à jour grâce au système de migrations Alembic.

### Commandes utiles

```bash
# Voir les logs en temps réel
docker-compose logs -f

# Logs uniquement du backend
docker-compose logs -f backend

# Redémarrer les services
docker-compose restart

# Arrêter l'application
docker-compose down

# Arrêter et supprimer les données (⚠️ perd toutes les données!)
docker-compose down -v
```

## Structure du projet

```
Pinarr/
├── backend/              # API FastAPI (Python)
│   ├── alembic/          # Migrations de base de données
│   ├── alembic.ini       # Configuration Alembic
│   ├── auth.py           # Authentification
│   ├── database.py       # Configuration DB
│   ├── main.py           # Application FastAPI
│   ├── models.py         # Modèles SQLAlchemy
│   ├── schemas.py        # Schémas Pydantic
│   └── services/         # Services métier
├── frontend/             # Application Vue.js 3
│   ├── src/
│   │   ├── components/   # Composants réutilisables
│   │   ├── views/        # Pages de l'application
│   │   └── services/     # Services API
│   └── nginx.conf        # Configuration Nginx
├── data/                 # Base de données SQLite (persistante)
├── uploads/              # Images uploadées (persistantes)
├── docker-compose.yml    # Configuration Docker
└── .env                  # Configuration environnement
```

## Sauvegarde des données

Vos données sont stockées dans deux dossiers :

- `./data/` : Base de données SQLite (`pinarr.db`)
- `./uploads/` : Images des bouteilles

**Pour sauvegarder :**

```bash
# Créer une archive de sauvegarde
tar -czf backup-pinarr-$(date +%Y%m%d).tar.gz data/ uploads/
```

**Pour restaurer :**

```bash
# Extraire la sauvegarde
tar -xzf backup-pinarr-YYYYMMDD.tar.gz

# Redémarrer
docker-compose restart
```

## Développement

### Créer une migration de base de données

Si vous modifiez les modèles (`backend/models.py`), vous devez créer une migration :

```bash
# Se connecter au container
docker-compose exec backend bash

# Générer la migration automatiquement
cd /app
alembic revision --autogenerate -m "description du changement"
```

Voir le guide complet dans [MIGRATIONS.md](./MIGRATIONS.md)

## Sécurité

- ⚠️ **Changez le mot de passe admin par défaut** immédiatement après l'installation
- 🔒 Le fichier `.env` contient vos secrets - ne le commitez jamais
- 🛡️ Vos données sont dans `./data/` et `./uploads/` - sauvegardez-les régulièrement

## Licence

MIT License

---

**Made with ❤️ for wine lovers** 🍷

[GitHub](https://github.com/jjllrrvvrr/Pinarr) | [Issues](https://github.com/jjllrrvvrr/Pinarr/issues)
