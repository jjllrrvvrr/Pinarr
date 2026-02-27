# Pinarr - Installation Homelab

## Installation rapide

1. **Cloner le repo**
   ```bash
   git clone <repo>
   cd sudowine
   ```

2. **Configurer l'IP**
   ```bash
   # Éditer le fichier .env
   nano .env
   ```
   
   Modifier uniquement cette ligne :
   ```
   HOST_IP=192.168.0.42  # ← Remplacez par votre IP
   ```

3. **Lancer l'application**
   ```bash
   docker compose up -d
   ```

4. **Accéder à l'application**
   - Ouvrir : `http://192.168.0.42:8908` (remplacez par votre IP)
   - Login : `admin`
   - Mot de passe : `admin123`

## Commandes utiles

```bash
# Voir les logs
docker compose logs -f

# Redémarrer
docker compose restart

# Mettre à jour
docker compose down
docker compose pull  # si images sur registry
docker compose up -d

# Arrêter
docker compose down
```

## Variables d'environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `HOST_IP` | **Obligatoire** | IP de votre serveur |
| `BACKEND_PORT` | 9994 | Port interne backend |
| `FRONTEND_PORT` | 8908 | Port exposé (changez si besoin) |
| `ADMIN_USERNAME` | admin | Login admin |
| `ADMIN_PASSWORD` | admin123 | Mot de passe admin |

## Données persistantes

Les données sont stockées dans :
- `./data/` : Base de données SQLite
- `./uploads/` : Images des bouteilles

## Dépannage

**Problème :** Le frontend ne se connecte pas au backend
- Vérifiez que `HOST_IP` est correctement configuré dans `.env`
- Vérifiez que le port 8908 est ouvert sur votre firewall

**Problème :** Accès refusé
- Attendre 10-20 secondes après le lancement pour l'initialisation
- Vérifier les logs : `docker compose logs backend`

**Changer les ports :**
```bash
# Éditer .env
FRONTEND_PORT=8080  # ou autre port
```

## Structure

```
sudowine/
├── docker-compose.yml      # Configuration Docker
├── .env                    # Variables (à modifier)
├── data/                   # Base de données (créé auto)
├── uploads/                # Images (créé auto)
├── backend/                # API FastAPI
└── frontend/              # Interface Vue.js
```
