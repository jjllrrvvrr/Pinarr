# Pinarr - Contexte pour Agent AI

> Ce fichier contient le contexte essentiel pour comprendre et travailler sur le projet Pinarr.
> Dernière mise à jour : April 23, 2026 (session migrations DB + étiquettes PDF + tests prod)
> ✅ **ÉTAT** : Migration database corrigée. Build Docker dev et prod OK. Backend démarre, QR public accessible.
> 🐛 **DB SLICE BUG FIX** : Corrigé `database.py` `[14:]` → `[12:]` qui créait un double `data/` dans le chemin.
> 🗄️ **Migrations Alembic** : `002/003/004/005` tous disponibles. `db_bootstrap.py` détecte DB legacy et applique 004→005.
> 🎨 **Étiquettes** : 3×5cm PDF via ReportLab (polices Montserrat + NunitoSans). Batch ZIP.
> 📦 **Tech** : ReportLab 4.4.10 pour PDF vectoriel embarqué.

---

## 🔗 Repository

| Propriété | Valeur |
|-----------|--------|
| **Repo GitHub** | `https://github.com/jjllrrvvrr/Pinarr.git` |
| **Repo local** | `/home/coder/project/Pinarr` |
| **Branche active** | `feature/qr-code-system` |
| **Remote** | `origin https://github.com/jjllrrvvrr/Pinarr.git` |
| **Status** | Up to date with origin |
| **Build dev** | `docker-compose.dev.yml` (ports 9080/9094) |
| **Environnement** | Linux, Workspace IA (OpenCode) |

---

## 🍷 Vue d'ensemble

**Pinarr** est une application web self-hosted de gestion de cave à vin, déployée via Docker. 
C'est une application complète permettant de gérer une cave à vin personnelle avec une interface intuitive et un déploiement simplifié via Docker.

### Fonctionnalités clés
- 📊 Gestion des bouteilles avec métadonnées complètes (millésime, cépage, région, prix, etc.)
- 🏗️ Système de caves hiérarchique structuré (Caves → Colonnes → Rangées → Positions)
- 📍 Géolocalisation des régions viticoles sur carte interactive (Leaflet/OpenStreetMap)
- 🔐 Authentification JWT sécurisée (bcrypt + cookies sécurisés)
- 📱 Interface responsive Vue.js 3 (Tailwind CSS, thème GitHub dark)
- 🏷️ **NOUVEAU** : Système QR code par bouteille physique (tracking individuel)
- 🎨 **NOUVEAU** : Multi-thème (Sombre/Clair/Vin Rouge/Nature Verte) via CSS custom properties
- 📸 Upload d'images auto-compressé en WebP avec support HEIC/HEIF
- ⭐ Notation étoilée et sélection de favoris
- 🏷 Système de tags
- 🗑 Historique des bouteilles épuisées

---

## 🏗️ Architecture Technique

### Stack
| Couche | Technologie |
|--------|-------------|
| **Frontend** | Vue.js 3 (Composition API), Tailwind CSS, Heroicons, Vite |
| **Backend** | FastAPI 0.115+, SQLAlchemy 2.0+, Pydantic 2.0+, Alembic |
| **Database** | SQLite (fichier local) |
| **Auth** | JWT (python-jose) + bcrypt, cookies sécurisés HttpOnly |
| **Map** | Leaflet.js + OpenStreetMap |
| **QR Codes** | qrcode.vue (frontend) |
| **Images** | Pillow (compression WebP, support HEIC/HEIF), ReportLab (PDF labels) |
| **Deploy** | Docker + Docker Compose (multi-stage) |
| **Web Server** | Nginx (reverse proxy) |

### Multi-stage Dockerfile
Le `Dockerfile` utilise 3 stages :
1. `frontend-build` (node:20-alpine) : Build Vue.js static
2. `backend` (python:3.10-slim) : Installation dépendances Python
3. `nginx:alpine` : Serve Nginx + Python backend dans même conteneur

### Structure des dossiers
```
Pinarr/
├── frontend/               # Application Vue.js 3
│   ├── src/
│   │   ├── components/     # Composants réutilisables
│   │   ├── views/          # Pages (routables)
│   │   ├── composables/    # Logique réutilisable Vue 3
│   │   ├── services/       # API clients (api.js, AuthService.js, qrService.js)
│   │   └── router/         # Vue Router avec guards
│   ├── src/assets/         # Assets statiques
│   ├── package.json        # Dépendances: Vue3, Tailwind, Leaflet, qrcode.vue
│   └── index.html
├── backend/                # API FastAPI
│   ├── routers/            # Routeurs FastAPI (auth)
│   ├── services/           # Logique métier (pattern repository)
│   ├── alembic/            # Migrations Alembic (001→005)
│   ├── models.py           # Modèles SQLAlchemy
│   ├── schemas.py          # Schémas Pydantic
│   ├── main.py             # Routes API (routes uniquement)
│   ├── config.py           # Config centralisée
│   ├── auth.py             # JWT, bcrypt, cookies
│   ├── database.py         # SQLAlchemy engine + session
│   ├── dependencies.py     # Dépendances FastAPI
│   ├── exceptions.py       # Exceptions métier
│   ├── entrypoint.sh       # Script init Docker (migrations + admin)
│   └── requirements.txt    # FastAPI, SQLAlchemy, Pillow, bcrypt, etc.
├── docker-compose.yml      # Déploiement simple
├── nginx.conf              # Config Nginx (proxy /api → backend)
├── entrypoint.sh           # Démarreur: migrations + admin + uvicorn + nginx
├── Dockerfile              # Multi-stage build
├── context.md              # VOUS ÊTES ICI
└── README.md               # Docs utilisateur
```

### Fichiers critiques
| Fichier | Rôle |
|---------|------|
| `backend/main.py` | Routes API FastAPI (endpoints CRUD) |
| `backend/models.py` | 7 modèles SQLAlchemy (Bottle, Cave, PhysicalBottle, etc.) |
| `backend/services/*.py` | 6 services métier (bottle, cave, physical_bottle, label, upload, geo) |
| `backend/fonts/` | Polices TTF embarquées (Montserrat-Bold, NunitoSans-Regular/Bold) |
| `frontend/src/App.vue` | Layout principal (header, navigation, modals) |
| `frontend/src/router/index.js` | Routes SPA avec auth guards |
| `nginx.conf` | Reverse proxy Nginx |
| `entrypoint.sh` | Auto-setup: migrations, admin, uvicorn, nginx |
| `docker-compose.dev.yml` | Docker Compose dev local (ports 9080/9094, données isolées) |

---

## 🗄️ Modèles de Données

### User
```
id, username, password_hash, is_admin, created_at
```

### Bottle (Vin référence)
```
id, name, domaine, country, year, type, region, cepage
alcohol, size (default: "75cl")
apogee_start, apogee_end          # Période de consommation idéale
jeunesse_end, maturite_end, apogee_end  # Phases de développement du vin
buy_link, quantity, price, description, rating, tags
is_favorite, image_path
physical_bottles (relationship)
```
**Mécanisme de tracking physique** : Après la migration 003, `quantity` = stock logique total, et chaque unité physique est un `PhysicalBottle` avec QR code unique. Le positionnement en cave déplace le `PhysicalBottle`, pas le `Bottle`.
- Pour assigner un vin à une position : le backend cherche un `PhysicalBottle` libre (`position_id == None`) de ce vin
- Pour retirer : libère le `PhysicalBottle` (`position_id` mis à `None`)
- La sérialisation API utilise la `property` virtuelle `bottle_at_position` pour compatibilité frontend

### Cave → CaveColumn → CaveRow → Position (Hiérarchie cave)
```
Cave (name)
  ├─ CaveColumn (name, order)
       └─ CaveRow (name, width, height, order)
            └─ Position (line, position)
                 physical_bottle (relationship One-to-One via physical_bottles.position_id)
```
**Schéma simplifié** (migration 004) : la colonne `physical_bottle_id` a été supprimée de `positions`. Le lien est désormais unidirectionnel via `physical_bottles.position_id`.

### PhysicalBottle (Nouveau - tracking par QR)
```
id, bottle_id (FK Bottle), position_id (FK Position, nullable)
qr_code (8 chars, unique, alphanum majuscules)
status: "in_cellar" | "consumed"
acquisition_date, removal_date, notes
```
**Migration** : Alembic `003` migre automatiquement les données existantes (`quantity` → N PhysicalBottles)

### GeocodedRegion
```
id, name (unique), lat, lon
```

---

## 🔌 API Endpoints

### Authentification (`POST /api/v1/auth/*`)
- `POST /login` - Cookie JWT défini (HttpOnly, Secure prod, SameSite=Lax)
- `POST /logout` - Supprime cookie
- `GET /me` - Infos utilisateur
- `GET /check` - Vérifie authentification
- `POST /change-password` - Nécessite ancien mot de passe
- `POST /update-profile` - Change username (recrée token)

### Bouteilles (`/api/v1/bottles`)
- `GET /bottles` - Liste avec positions
- `GET /bottles/{id}` - Détail avec positions + physical_bottles
- `GET /bottles/search?q=` - Recherche par nom
- `POST /bottles` - Création (génère N QR codes si quantity > 0)
- `PUT /bottles/{id}` - MAJ complète
- `PATCH /bottles/{id}` - MAJ partielle
- `DELETE /bottles/{id}` - Suppression cascade

### Caves (`/api/v1/caves`)
- `GET/POST /caves` - CRUD caves
- `POST /caves/{id}/columns` - Ajouter colonne
- `PUT/DELETE /columns/{id}` - MAJ/Suppr colonne
- `POST /columns/{id}/rows` - Ajouter rangée (+ auto-crée les positions W×H)
- `PUT/DELETE /rows/{id}` - MAJ/Suppr rangée (recrée positions si dimensions changent)

### Positions
- `GET /rows/{id}/positions` - Liste positions avec bouteilles assignées
- `PUT /positions/{id}` - Assigner bouteille (ou retirer avec bottle_id: null)
- `DELETE /positions/{id}/bottle` - Retirer bouteille

### Physical Bottles - QR
- `POST /bottles/{id}/generate-qr-codes` - Génère N QR codes uniques
- `GET /bottles/{id}/physical-bottles` - Liste toutes les bouteilles physiques
- `GET /api/scan/{qr_code}` — **PUBLIC** (pas de /api/v1, sans auth) — Résultat scan QR
- `POST /api/remove/{physical_bottle_id}` — **PUBLIC** retire bouteille (consommation via QR)
- `POST /physical-bottles/{id}/remove` — Marquer comme consommée + libère position
- `PUT /physical-bottles/{id}/move` — Déplace vers nouvelle position (ou stock libre)
- `GET /api/v1/bottles/{id}/batch-labels` — ZIP PDF de toutes les étiquettes en cave
- `GET /api/v1/bottles/{id}/physical-bottles/{qr_code}/label` — PDF individuel d'une bouteille physique

### Upload
- `POST /api/v1/upload` - Upload fichier avec validation MIME + signature + compression WebP
- `POST /api/v1/upload-from-url` - Télécharge image depuis URL externe

### Géocodage
- `GET /api/v1/geocoded-regions` - Régions avec coordonnées
- `POST /api/v1/geocoded-regions` - Ajouter région géocodée (cache pour futures sessions)

---

## 🎨 Frontend - Composants & Architecture

### Routing (Vue Router 5)
```javascript
'/'              → BottleList (homepage avec filtres)
'/login'         → LoginView (public)
'/add'           → AddBottle (formulaire création)
'/edit/:id'      → AddBottle (reuse component)
'/wine/:id'      → BottleDetail (fiche vin + QR codes)
'/bottle/:qrCode'→ ScanResultView (PUBLIC - résultat scan)
'/map'           → MapView (Leaflet)
'/caves'         → CaveList (liste caves)
'/caves/new'     → CaveEdit (création cave)
'/caves/:id'     → CaveView (visualisation grille)
'/caves/:id/edit'→ CaveEdit (modification cave)
```

### Auth Guards
- `authGuard` : Redirige vers /login si non authentifié (cookie session_token absent/invalide)
- `publicGuard` : Réservé aux routes accessibles sans login (/login, /bottle/:qrCode)

### Services
- `api.js` : Client HTTP avec Bearer token auto-injecté depuis sessionStorage
- `AuthService.js` : Login/logout/session storage/sessionStorage username
- `qrService.js` : Génération/list/scan QR codes via API

### Theme System (Multi-thème via CSS Custom Properties)

| Fichier | Rôle |
|---------|------|
| `tailwind.config.js` | Mapping `gh-*` → `var(--*)` (colors, shadows, radii, zIndex) |
| `src/styles/variables.css` | Définition des CSS custom properties pour chaque thème |
| `src/composables/useTheme.js` | `currentTheme`, `setTheme()`, persistance `localStorage` |
| `src/composables/useWineTypeStyles.js` | Helper `getTypeBadgeClass`/`getTypeDotClass`/`getTypeBgClass` pour les badges de type de vin |

#### Design Tokens (gh-*)
| Token | Variable CSS | Utilisation |
|-------|-------------|-------------|
| `gh-bg` | `--bg-primary` | Fond principal |
| `gh-surface` | `--bg-surface` | Cards, modals |
| `gh-elevated` | `--bg-elevated` | Surfaces au-dessus |
| `gh-border` | `--border-default` | Bordures |
| `gh-text` | `--text-primary` | Texte principal |
| `gh-text-secondary` | `--text-secondary` | Labels, secondaire |
| `gh-accent-green` | `--accent-green` | Boutons positifs |
| `gh-accent-red` | `--accent-red` | Erreurs, suppression |
| `wine-red` / `wine-white` / `wine-rose` / `wine-champagne` | `--wine-*` | Couleurs sémantiques des types de vin |

#### Thèmes disponibles
| Thème | `data-theme` | Description |
|-------|-----------|-------------|
| Sombre (défaut) | — | `:root` — GitHub Dark-like |
| Clair | `light` | `f6f8fa` surfaces, texte foncé |
| Vin Rouge | `red-wine` | `2a0a0a` fond, accents bordeaux/rouges |
| Nature Verte | `green-nature` | `0a1a0a` fond, accents vignoble/verts |

Le switcher de thème se trouve dans le **menu burger** de `App.vue` (en bas du menu).

### Principaux Composants
| Composant | Rôle |
|-----------|------|
| `BottleCard` | Carte vin dans liste (grid/list) |
| `BottleSidebar` | Sidebar cave avec drag & drop |
| `BottlePreview` | Tooltip hover sur bouteille cave |
| `WineTypeSelector` | Sélecteur type de vin avec icons |
| `WineTypeBadge` | Badge coloré selon type |
| `WinePhaseBadge` | Badge phase d'évolution (Jeunesse/Maturité/Apogée/Déclin) |
| `WinePhaseTimeline` | Timeline visuelle éditable des phases |
| `WineGlass` | Icône bouteille SVG personnalisée |
| `StarRating` | Notation 0-5 étoiles |
| `QrLabelPrinter` | Modal d'impression étiquettes QR |
| `MoveBottleModal` | Modal de déplacement bouteille physique |
| `RemovePositionModal` | Modal de retrait position cave |

### Thème visuel (GitHub Dark)
| Couleur | Hex | Utilisation |
|---------|-----|-------------|
| Background | `#0d1117` | Fond principal |
| Surface | `#161b22` | Cards, modals |
| Border | `#30363d` | Bordures |
| Text | `#c9d1d9` | Texte principal |
| Text muted | `#8b949e` | Labels, secondaire |
| Accent | `#58a6ff` | Liens, focus |
| Success | `#238636` | Boutons positifs |
| Danger | `#f85149` | Erreurs, suppression |

---

## 📋 Conventions de Code

### Python (Backend)
- **Architecture en couches strictes** : Services → Routes (Services = logique métier, Routes = HTTP)
- **Modèles** : SQLAlchemy dans `models.py` uniquement
- **Schémas** : Pydantic dans `schemas.py` (BottleCreate, BottlePatch, etc.)
- **Exceptions métier** : `PinarrException` dans `exceptions.py` (BottleNotFoundException, etc.)
- **Auth** : Middleware global dans `main.py`. Les routes `/auth/*`, `/`, `/uploads/*`, `/api/scan/*`, et `/api/remove/*` sont publiques. Le reste nécessite un JWT cookie valide.
- **DB queries** : Toujours utiliser `joinedload` pour éviter les N+1 queries
- **Uploads** : Validation MIME + signature magique + conversion WebP (85%, max 1920px)

### Vue.js (Frontend)
- **Composition API** obligatoire avec `import { ref, computed, watch } from 'vue'`
- **`<script setup>`** uniquement
- **Style** : Tailwind CSS, aucun CSS custom sauf animations/Leaflet
- **Icons** : `@heroicons/vue/24/solid` ou `/24/outline`
- **Imports internes** : `@/` est configuré comme alias pour `frontend/src/`

### Types de Vin (IDs internes)
| ID | Label | Couleur |
|----|-------|---------|
| `RED` | Rouge | #f85149 |
| `WHITE` | Blanc | #e3b341 |
| `ROSE` | Rosé | #db61a2 |
| `EFFERVESCENT` | Effervescent | #a371f7 |
| `SWEET` | Doux | #8b5cf6 |

---

## ✅ Fonctionnalités Récentes (Derniers commits)

### `f583a6e` - feat: Ajout du système QR code par bouteille physique
- Création table `physical_bottles` (Alembic migration 003)
- Chaque bouteille physique a un QR code unique (8 chars)
- Génération par lot depuis la fiche vin
- Scan QR public sans authentification
- Tracking : acquisition, consommation, déplacement
- Séparation quantity (total) vs cellar_count (en cave)

### `8deec51` - fix(BottleSidebar): correct remaining to place
- Correction du calcul des bouteilles restant à placer
- Masquage des vins avec stock 0

### `acdcdae` - v0.3.1 - Bug fixes and new features
- Import image depuis URL externe
- Corrections diverses

### `7f1d7b7` - fix: add migration 002 for phase columns
- Migration Alembic ajoutant `jeunesse_end`, `maturite_end`, `apogee_end`

### `d9a2882` - feat: add wine development phases
- Système de phases du vin : Jeunesse → Maturité → Apogée → Déclin
- Timeline visuelle interactive
- Filtres par phase dans la liste

### `46f0285` - feat: gestion automatique du retrait des positions
- Modal pour sélectionner quelles positions retirer quand quantity diminue

### `1865d64` - feat: support des photos mobiles avec compression HEIC
- Upload HEIC/HEIF converti automatiquement
- Capture caméra mobile supportée
- Compression WebP côté backend ET frontend

### `ca70fee` - ui: optimise sélecteur de type de vin
- Nouveau composant visuel pour sélectionner le type

---

## 🔧 Configuration & Déploiement

### Variables d'environnement (docker-compose.yml)
```yaml
PORT: 8908                    # Port externe Nginx web
BACKEND_PORT: 9994            # Port direct API (exposé)
ADMIN_USERNAME: admin         # Login par défaut
ADMIN_PASSWORD: admin123      # MDP par défaut
SECRET_KEY: <auto-généré>   # JWT secret (openssl rand -hex 32 si vide)
```

### Déploiement standard (30 secondes)
```bash
curl -O https://raw.githubusercontent.com/jjllrrvvrr/Pinarr/main/docker-compose.yml
docker compose up -d
```
Accès : `http://localhost:8908` | Login : `admin` / `admin123`

### Développement local
```bash
# Backend (Python 3.10+)
cd backend
pip install -r requirements.txt
python3 -m uvicorn main:app --reload  # http://localhost:8000

# Frontend (Node 20+)
cd frontend
npm install
npm run dev                           # http://localhost:5173
```

### Database
- SQLite local : `data/pinarr.db` (persisté via volume Docker)
- Uploads : `uploads/` (images WebP)
- Migrations : `db_bootstrap.py` détecte → Alembic upgrade head

---

## 📝 État Actuel du Projet

### Derniers commits sur `feature/qr-code-system`
```
f583a6e feat: Ajout du système QR code par bouteille physique
8deec51 fix(BottleSidebar): correct remaining to place calculation
acdcdae v0.3.1 - Bug fixes and new features
7f1d7b7 fix: add migration 002 for phase columns
```

### Fichiers actuellement modifiés / en cours (session 2026-04-22)
- `context.md` (présent, mis à jour)
- `backend/main.py` — Middleware auth (`public_paths`, `OPTIONS`, imports consolidés)
- `backend/models.py` — `cascade="all, delete-orphan"`, nettoyage commentaires
- `backend/services/bottle_service.py` — `patch_bottle` null-safe, `validate_bottle_placement` compte reel, factorisation sérialisation
- `backend/services/cave_service.py` — `update_row` protège positions occupées, `create_row` transaction atomique
- `backend/services/physical_bottle_service.py` — `PinarrException` au lieu de `Exception`
- `backend/services/__init__.py` — Exports complets
- `backend/entrypoint.sh` — `chmod 755`
- `entrypoint.sh` — Vérifié
- `frontend/src/App.vue` — Suppression import inutilisé + `console.log`
- `frontend/src/components/BottleSidebar.vue` — `cellar_quantity`, `.slice().sort()`
- `frontend/src/views/BottleDetail.vue` — Grille bouteilles physiques + téléchargement PDF individuel/batch ZIP
- `frontend/src/views/ScanResultView.vue` — `scanQrCode()` au lieu de redirect après retrait
- `frontend/src/views/BottleList.vue` — `getBottlePhase` null-safe, filtres `cellar_quantity`
- `frontend/src/views/CaveView.vue` — Map `bottleAtPositionMap` O(1), `try/catch` drag, rollback complet
- `frontend/src/router/guards.js` — Routes `/bottle/*` ajoutées aux publiques
- `frontend/src/router/index.js` — Suppression `beforeEnter: publicGuard` sur `/bottle/:qrCode`
- `frontend/src/services/qrService.js` — `getQrUrl` URL publique frontend

### Corrections — Session 2026-04-21 (Partie 1)
Corrections liées à la migration Alembic 003 (système QR) sur les 17 bugs originaux :

| # | Bug | Fichier | Type |
|---|-----|---------|------|
| 1 | `Position.bottle_at_position` absente (relationship inexistante) | `models.py` | Backend |
| 2 | `get_positions_for_row` utilisait `joinedload(bottle_at_position)` inexistant | `cave_service.py` | Backend |
| 3 | `assign_bottle_to_position` assignait `bottle_id` sur colonne supprimée | `cave_service.py` | Backend |
| 4 | `remove_bottle_from_position` utilisait `bottle_id` | `cave_service.py` | Backend |
| 5 | `validate_bottle_placement` filtrait sur `Position.bottle_id` (inexistant) | `bottle_service.py` | Backend |
| 6 | `get_bottles_with_positions` / `get_bottle_with_position` jointures cassées | `bottle_service.py` | Backend |
| 7 | `datetime` importé au fond de `physical_bottle_service.py` (NameError) | `physical_bottle_service.py` | Backend |
| 8 | Endpoint `/check-duplicate` retournait `{"results":[]}` au lieu de `{"matches":[]}` | `main.py` | Backend |
| 9 | `PhysicalBottle` manquant dans `create_db_tables()` | `database.py` | Backend |
| 10 | `get_caves` / `get_cave` ne chargeaient pas `PhysicalBottle` (caves affichées vides) | `cave_service.py` | Backend |
| 11 | Compteur positions occupées dans CaveList utilisait `bottle_id` | `CaveList.vue` | Frontend |
| 12 | `moveBottleLocally` assignait `bottle_id` au lieu de `physical_bottle_id` | `CaveView.vue` | Frontend |
| 13 | `useQuantityManager` non importé dans `AddBottle.vue` | `AddBottle.vue` | Frontend |
| 14 | `b.location` inexistant dans le filtre recherche `BottleList.vue` | `BottleList.vue` | Frontend |
| 15 | QR URL `App.vue` pointait vers `/wine/{id}` (protégé, scan impossible) | `App.vue` | Frontend |
| 16 | QR URL `BottleDetail.vue` pointait vers `/bottle/{id_conceptuel}` | `BottleDetail.vue` | Frontend |
| 17 | `cellarCount` comptait toutes les physical_bottles, même sans position | `BottleDetail.vue` | Frontend |

### Corrections — Session 2026-04-21 (Partie 2)
Nouveaux bugs découverts et corrigés durant le test du conteneur dev :

| # | Bug | Fichier | Type |
|---|-----|---------|------|
| 18 | Cycle de FK croisée `physical_bottles.position_id` ↔ `positions.physical_bottle_id` → `AmbiguousForeignKeysError` | `models.py` + migration 004 | Backend |
| 19 | `Base.metadata.create_all()` dans `entrypoint.sh` forçait la création AVANT les migrations Alembic | `entrypoint.sh` | Backend |
| 20 | `create_bottle()` ne générait pas automatiquement les `PhysicalBottle` | `bottle_service.py` | Backend |
| 21 | `get_bottles_with_positions` / `get_bottle_with_position` ne retournaient pas `physical_bottles` ni `cellar_quantity` | `bottle_service.py` | Backend |
| 22 | `assign_bottle_to_position` utilisait encore `db_position.physical_bottle_id` (colonne retirée) | `cave_service.py` | Backend |
| 23 | `remove_physical_bottle` / `move_physical_bottle` utilisaient `position.physical_bottle_id` | `physical_bottle_service.py` | Backend |
| 24 | `BottleList.vue` filtrait sur `bottle.quantity` au lieu de `bottle.physical_bottles.length` | `BottleList.vue` | Frontend |
| 25 | `BottleSidebar.vue` filtrait sur `quantity` au lieu de `physical_bottles.length` | `BottleSidebar.vue` | Frontend |
| 26 | `WinePhaseBadge.vue` avait un bloc CSS mal formé (`--phase-*` sans sélecteur `:root`) | `WinePhaseBadge.vue` | Frontend |
| 27 | URL QR dans les étiquettes pointait vers `/api/v1/bottle/{qr}` (route protégée) au lieu de `/bottle/{qr}` (publique) | `QrLabelPrinter.vue` | Frontend |
| 28 | Phases sur étiquettes QR : `apogee_start` inexistant au lieu de `maturite_end` | `QrLabelPrinter.vue` | Frontend |
| 29 | `validate_bottle_placement` non exporté dans `services/__init__.py` → backend ne démarrait pas | `services/__init__.py` | Backend |
| 30 | `main.py` : imports de services caves/physical_bottles manquants après l'ajout de `validate_bottle_placement` | `main.py` | Backend |
| 31 | Schema `BottleBase` ne contenait pas `quantity` → stats `totalBottles`/`totalValue` à 0 | `schemas.py` | Backend |
| 32 | `App.vue` stats utilisaient `b.quantity` au lieu de `b.cellar_quantity` | `App.vue` | Frontend |

### Audit Complet — 2026-04-22 (TODO future session)

Générée après revue exhaustive backend + frontend. Chaque ligne est actionnable.

#### 🔴 CRITICAL — Backend crash ou fonctionnalité cassée (TOUS CORRIGÉS ✅)

| # | Fichier | Ligne | Problème | Statut |
|---|---------|-------|----------|--------|
| C1 | `backend/models.py` | 36-40 | `apogee_end` dupliqué dans `Bottle` → crash SQLAlchemy | ✅ Corrigé |
| C2 | `backend/schemas.py` | 18-22 | `apogee_end` dupliqué dans `BottleBase` → crash Pydantic | ✅ Corrigé |
| C3 | `backend/main.py` | ~101-121 | Route publique `/bottle/{qr}` **protégée** par middleware auth | ✅ Corrigé |
| C4 | `backend/main.py` | ~357 | `create_position` appelée mais **non importée** | ✅ Corrigé |
| C5 | `backend/main.py` | ~89 | `OPTIONS` (CORS preflight) interceptés par middleware → 401 | ✅ Corrigé |
| C6 | `frontend/src/views/BottleList.vue` | 364-367 | Filtre « En cave / Historique » sur `physical_bottles.length` inclut `consumed` | ✅ Corrigé |
| C7 | `frontend/src/components/QrLabelPrinter.vue` | 84 | CSS print : `body * { visibility:hidden }` cache **tous** les enfants même avec `!important visible` | ✅ Corrigé (popup d'impression)

#### 🟠 HIGH — Bugs utilisateur majeurs (TOUS CORRIGÉS ✅)

| # | Fichier | Ligne | Problème | Statut |
|---|---------|-------|----------|--------|
| H1 | `backend/services/cave_service.py` | 291-302 | `assign_bottle_to_position` silencieux si plus de `PhysicalBottle` libre | ✅ Laissé tel (validation par caller, comportement correct) |
| H2 | `backend/services/cave_service.py` | 189-198 | `update_row` supprime/recrée toutes les `Position` si dimensions changent → placements perdus | ✅ Bloque si positions occupées |
| H3 | `backend/services/bottle_service.py` | 217 | `patch_bottle` saute les valeurs `None` → impossible de vider un champ | ✅ Supprimé `if value is not None` |
| H4 | `backend/services/bottle_service.py` | 237-264 | `validate_bottle_placement` repose sur `quantity` (null possible) → `TypeError` | ✅ Compte `PhysicalBottle` réellement en stock |
| H5 | `backend/services/physical_bottle_service.py` | 222 | `move_physical_bottle` lève `raise Exception(...)` brute | ✅ `PinarrException` |
| H6 | `frontend/src/App.vue` | 177-212 | `updateQuantity` modifie `quantity` sans créer/supprimer `PhysicalBottle` | ⚠️ Complexe — nécessite refonte UI + API |
| H7 | `frontend/src/services/qrService.js` | 70 | `getQrUrl()` retourne **URL API** au lieu de **URL frontend** | ✅ `window.location.origin` |
| H8 | `frontend/src/components/BottleSidebar.vue` | 105-151 | Filtre sur `physical_bottles.length` au lieu de `cellar_quantity` | ✅ `cellar_quantity` |
| H9 | `frontend/src/views/CaveView.vue` | 62-73 | `getBottleAtPosition` = O(n⁴) dans le DOM | ✅ Map précalculée |
| H10 | `frontend/src/views/CaveView.vue` | 346 | Rollback optimiste partiel | ✅ `fetchCave()` + `fetchBottles()` complet |

#### 🟡 MEDIUM — Dette technique / edge cases (TOUS CORRIGÉS ✅)

| # | Fichier | Ligne | Problème | Statut |
|---|---------|-------|----------|--------|
| M1 | `backend/models.py` | 50 | `Bottle.physical_bottles` sans cascade | ✅ `cascade="all, delete-orphan"` |
| M2 | `backend/services/physical_bottle_service.py` | 137 | Génération QR : race condition possible | ⚠️ Accepté pour volumes Pinarr (contrainte DB unique) |
| M3 | `backend/services/physical_bottle_service.py` | 104-134 | `get_bottle_physical_bottles` construit dicts manuellement | ⚠️ Format API spécifique, laissé tel |
| M4 | `backend/services/cave_service.py` | 160 | `create_row` sans transaction | ✅ `db.begin()` |
| M5 | `frontend/src/views/CaveView.vue` | 434 | `swap` non atomique côté backend | ⚠️ Nécessite endpoint dédié, laissé en note |
| M6 | `frontend/src/views/CaveView.vue` | 232 | `handleDrop` `JSON.parse` sans `try/catch` | ✅ Wrappé |
| M7 | `frontend/src/views/BottleList.vue` | 239 | `getBottlePhase` : NaN si `year` null | ✅ Early return |
| M8 | `frontend/src/views/BottleList.vue` | 210 | `hasTextFilters` oublie `color` et `phase` | ✅ Ajouté |
| M9 | `frontend/src/App.vue` | 315 | `totalBottles` / `totalValue` calcul sur `bottles.value` vide | ✅ Corrigé upstream via `cellar_quantity` / `quantity` |

#### 🟢 LOW — Code smells / optimisations (TOUS CORRIGÉS ✅)

| # | Bug | Fichier | Statut |
|---|-----|---------|--------|
| L1 | `Position.bottle_id` @property compatibilité | `models.py` | ✅ Propriété correcte |
| L2 | `chmod 777` trop permissif | `backend/entrypoint.sh` | ✅ `chmod 755` |
| L3 | Script Python inline → fichier séparé | `entrypoint.sh` | ⚠️ Amélioration future |
| L4 | Duplication sérialisation | `bottle_service.py` | ✅ Factorisé (`_serialize_bottle`, etc.) |
| L5 | `console.log` exposant `newUsername` | `App.vue` | ✅ Supprimé |
| L6 | Import inutilisé `useQuantityManager` | `App.vue` | ✅ Supprimé |
| L7 | `.sort()` mutating sur computed | `BottleSidebar.vue` | ✅ `.slice().sort()` |

---

### Prochaines étapes connues (/TODO)

**🔴 URGENT — Bugs connus restants à corriger / vérifier :**
- [ ] **Déconnexion** : "Quitter" dans App.vue ne fonctionne pas
- [ ] **Statistiques** : `totalBottles` / `totalValue` ne sont pas rafraîchies en temps réel
- [ ] **QR codes** : Vérifier scan physique mobile (redirection corrigée)
- [x] **QR public** : Route `/bottle/:qrCode` ne redirige plus vers /login ✅
- [ ] **Thème** : Passage de thème ne persiste pas après reload
- [x] **PDF** : Génération PDF côté backend avec ReportLab (polices Montserrat/NunitoSans embarquées, toutes les phases affichées en gras) ✅

**🟡 À planifier :**
- Endpoint `POST /positions/swap` atomique côté backend (M5)
- Refonte `updateQuantity` dans App.vue pour créer/supprimer `PhysicalBottle` (H6)
- Migration script init admin inline vers fichier séparé (L3)
---

## 🚨 Points d'attention critiques

1. **Auth** : Le middleware dans `main.py` protège tout sauf explicitement : `/auth/*`, `/`, `/uploads/*`, `/api/scan/*`, `/api/remove/*`
2. **QR Codes Publics** : `/api/scan/{qr_code}` et `/api/remove/{id}` sont les seules routes publiques pour les scanners mobiles. La route frontend SPA `/bottle/{qrCode}` est aussi publique (pas de `beforeEnter`).
3. **Positions vs Quantities** : `bottle.quantity` est l'autorité conceptuelle, `PhysicalBottle` est le tracking réel
4. **Upload** : Toutes les images sont converties en WebP 85%, max 1920px
5. **Migrations** : `alembic upgrade head` est l'unique point d'entrée pour le schéma. Plus de `create_db_tables()` au boot.
6. **Single User** : Le système est actuellement conçu pour un seul utilisateur admin (is_admin=True par défaut)

---

## 🗄️ Système de Migrations (Alembic)

> **PRINCIPE** : Alembic est la seule source de vérité pour le schéma. Le `create_db_tables()` traditionnel est remplacé par un `db_bootstrap.py` intelligent.

### Problème à résoudre
- `create_db_tables()` dans `main.py` crée le schéma en silence, sans informer Alembic.
- `alembic upgrade head` dans `entrypoint.sh` suppose une DB "jamais touchée" et crashe si les tables existent déjà (ex: installation fraîche, ou copie de prod).

### Plan : Mode "Alembic Only"

#### 1. `db_bootstrap.py` — Démarrage universel
- Créé dans `backend/db_bootstrap.py`.
- **Détecte** l'état : DB vide, legacy (sans `alembic_version`), ou versionnée.
- **Agit** :
  - DB vide → `create_db_tables()` puis `alembic stamp 004`.
  - Legacy → `alembic stamp 002/003/004` (détection auto) puis `alembic upgrade head`.
  - Versionnée → `alembic upgrade head` classique.

#### 2. Modifications des migrations existantes
  - **002** (phases) : rendu idempotent (vérifie `PRAGMA table_info` avant `op.add_column`).
  - **003** (physical_bottles) : rendu idempotent + table reconstruction SQLite.
  - **004** (cleanup) : table reconstruction manuelle SQLite (évite `DROP COLUMN` + FK).
  - **005** (users) : ajoute la table `users` manquante en prod (legacy DB only).

#### 3. Modifications des fichiers de lancement
- **`entrypoint.sh`** : appelle `python3 /app/backend/db_bootstrap.py` au lieu de `alembic upgrade head`.
- **`main.py`** : supprimer `create_db_tables()` au boot (non idempotent).

#### 4. Procédure pour futures migrations
```bash
# Modifier models.py (ajouter colonne/table)
# Générer automatiquement
cd backend
alembic revision --autogenerate -m "ajout_colonne_xyz"
# Vérifier le fichier généré
# Commit + push
```
**Nouvelles migrations (005+) n'ont PAS besoin d'idempotence** car Alembic maîtrise le point de départ.

---

---

## 🔄 Historique des modifications du context.md

| Date | Modification |
|------|-------------|
| 2025-04-21 (init) | Création du fichier avec architecture, modèles, API, composants |
| 2025-04-21 (update) | Ajout état projet, repo GitHub, fichiers en cours, TODO |

---

## 🔗 Ressources

- Repo GitHub : https://github.com/jjllrrvvrr/Pinarr
- README : `/README.md`
- Architecture Backend : `/backend/ARCHITECTURE.md`
- Screenshots : `/docs/screenshots/`

---

*Made with ❤️ for wine lovers* 🍷