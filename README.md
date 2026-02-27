# Pinarr 🍷

Application de gestion de cave à vin self-hosted avec Docker.

## Fonctionnalités

- 📊 **Gestion complète** : Bouteilles, caves, positions
- 🗺️ **Cartographie** : Visualisation géographique des régions viticoles  
- 🔐 **Authentification sécurisée** : Session-based avec tokens JWT
- 📱 **Responsive** : Interface web moderne (Vue.js 3)
- 🐳 **Docker-ready** : Déploiement en 2 commandes

## Installation Docker

### Prérequis

- Docker 20.10+
- Docker Compose 2.0+
- 512 Mo RAM

### Déploiement rapide

**1. Cloner le projet**

```bash
git clone https://github.com/jjllrrvvrr/Pinarr.git
cd Pinarr
```

**2. Configurer**

```bash
cp .env.example .env
# Éditer .env et changer:
# - ADMIN_PASSWORD (obligatoire!)
# - SECRET_KEY (générer avec: openssl rand -hex 32)
```

**3. Lancer**

```bash
docker-compose up -d
```

**4. Accéder**

- Web : `http://localhost:80`
- Login par défaut : `admin` / (mot de passe défini dans .env)

### Commandes utiles

```bash
# Voir les logs
docker-compose logs -f

# Redémarrer
docker-compose restart

# Arrêter
docker-compose down
```

## Structure du projet

```
Pinarr/
├── backend/           # API FastAPI (Python)
├── frontend/          # Vue.js 3 + Tailwind
├── docker-compose.yml # Configuration Docker
└── .env.example       # Configuration
```

## Licence

MIT License

---

**Made with ❤️ for wine lovers** 🍷
