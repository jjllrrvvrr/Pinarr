# 🍷 Pinarr

Application de gestion de cave à vin self-hosted avec Docker.

## Fonctionnalités

- 📊 Gestion des bouteilles, caves et positions
- 🗺️ Cartographie des régions viticoles
- 🔐 Authentification sécurisée
- 📱 Interface web responsive (Vue.js 3)
- 🐳 Déploiement Docker simple

## Installation rapide (30 secondes)

```bash
# Télécharger uniquement le docker-compose.yml
curl -O https://raw.githubusercontent.com/jjllrrvvrr/Pinarr/main/docker-compose.yml

# Lancer l'application
docker-compose up -d
```

Accès : `http://localhost:8908` | Login : `admin` / `admin123`

## Installation avec git

```bash
git clone https://github.com/jjllrrvvrr/Pinarr.git
cd Pinarr
docker-compose up -d
```

## Mise à jour

```bash
# Méthode rapide
docker-compose pull && docker-compose up -d

# Ou avec git
git pull && docker-compose pull && docker-compose up -d
```

## Configuration

Les variables d'environnement optionnelles dans `docker-compose.yml` :

| Variable | Défaut | Description |
|----------|--------|-------------|
| `PORT` | 8908 | Port de l'interface web |
| `ADMIN_USERNAME` | admin | Nom d'utilisateur admin |
| `ADMIN_PASSWORD` | admin123 | Mot de passe admin |
| `SECRET_KEY` | (auto) | Clé secrète JWT (générée auto) |

## Données persistantes

Les données sont stockées dans les volumes Docker :
- `./data/` : Base de données SQLite
- `./uploads/` : Images des bouteilles

---

**MIT License** - [GitHub](https://github.com/jjllrrvvrr/Pinarr)