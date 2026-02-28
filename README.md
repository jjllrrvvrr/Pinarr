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

Accès : `http://votre-ip:8908` | Login : `admin`

## Commandes

```bash
docker-compose logs -f     # Voir les logs
docker-compose restart     # Redémarrer
docker-compose down        # Arrêter
```

## Sauvegarde

```bash
tar -czf backup.tar.gz data/ uploads/
```

## Structure

```
Pinarr/
├── backend/      # API FastAPI
├── frontend/     # App Vue.js 3
├── data/         # Base de données SQLite
└── uploads/      # Images des bouteilles
```

---

**MIT License** - [GitHub](https://github.com/jjllrrvvrr/Pinarr)