# Pinarr 🍷

Application de gestion de cave à vin self-hosted avec Docker.

## Fonctionnalités

- 📊 Gestion des bouteilles, caves et positions
- 🗺️ Cartographie des régions viticoles
- 🔐 Authentification sécurisée
- 📱 Interface web responsive (Vue.js 3)
- 🐳 Déploiement Docker simple

## Installation

```bash
git clone https://github.com/jjllrrvvrr/Pinarr.git
cd Pinarr
# Modifier .env (HOST_IP et ADMIN_PASSWORD obligatoires)
docker-compose up -d
```

Accès : `http://localhost:8908` | Login : `admin`

## Mise à jour

```bash
# Récupérer les dernières modifications
git pull

# Rebuild et redémarrer (les données sont préservées)
docker-compose down
docker-compose up -d --build
```

---

**MIT License** - [GitHub](https://github.com/jjllrrvvrr/Pinarr)