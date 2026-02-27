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
```

**Variables obligatoires à modifier dans `.env` :**

```bash
# 1. HOST_IP - Votre IP locale (obligatoire!)
# Trouvez votre IP avec:
#   - Mac/Linux: ifconfig ou ip addr
#   - Windows: ipconfig
# Exemple: 192.168.1.100
HOST_IP=192.168.1.100

# 2. ADMIN_PASSWORD - Changez le mot de passe par défaut
ADMIN_PASSWORD=votre_mot_de_passe

# 3. SECRET_KEY - Générez une clé unique
# openssl rand -hex 32
SECRET_KEY=votre_cle_secrete_32_caracteres
```

**3. Lancer**

```bash
docker-compose up -d
```

**4. Accéder**

- Web : `http://localhost:8908`
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
