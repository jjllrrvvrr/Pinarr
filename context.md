# Pinarr - Contexte pour Agent AI

> Ce fichier contient le contexte essentiel pour comprendre et travailler sur le projet Pinarr.
> Dernière mise à jour : May 3, 2026 (après session : thèmes champagne + responsive + map fixes + fixes post-session)
> ✅ **ÉTAT** : Conteneur healthy. Build Docker OK. Thèmes Champagne (Clair/Sombre) actifs. Map avec fitBounds et pane markers fixé.
> 🐛 **DB SLICE BUG FIX** : Corrigé `database.py` `[14:]` → `[12:]` qui créait un double `data/` dans le chemin.
> 🗄️ **Migrations Alembic** : `002/003/004/005` tous disponibles. `db_bootstrap.py` détecte DB legacy et applique 004→005.
> 🎨 **Étiquettes** : 3×5cm PDF @ 300dpi. Polices Montserrat + NunitoSans. Batch ZIP.
> 📦 **Tech** : ReportLab 4.4.10 pour PDF vectoriel embarqué.
> ⚠️ **Fichiers non commit** : `backend/services/cave_service.py` (fix transaction SQLAlchemy), `frontend/src/views/BottleDetail.vue` (fix routing cave_id), `context.md` — prêts à committer.

---

## 🔗 Repository

| Propriété | Valeur |
|-----------|--------|
| **Repo GitHub** | `https://github.com/jjllrrvvrr/Pinarr.git` |
| **Repo local** | `/Users/julienlrvr/Documents/Pinarr` |
| **Branche active** | `main` |
| **Remote** | `origin https://github.com/jjllrrvvrr/Pinarr.git` |
| **Status** | Up to date with origin — **avec fichiers non commit** (fix cave_service.py + BottleDetail.vue + docs issues) |
| **Build dev** | `docker-compose.dev.yml` (ports 9080/9094) |
| **Environnement** | macOS, Docker Desktop |

---

## 🍷 Vue d'ensemble

**Pinarr** (frontend branding: **Pinaar**) est une application web self-hosted de gestion de cave à vin, déployée via Docker.

### Fonctionnalités clés
- 📊 Gestion des bouteilles avec métadonnées complètes (millésime, cépage, région, prix, etc.)
- 🏗️ Système de caves hiérarchique structuré (Caves → Colonnes → Rangées → Positions)
- 📍 Géolocalisation des régions viticoles sur carte interactive (Leaflet/OpenStreetMap)
- 🔐 Authentification JWT sécurisée (bcrypt + cookies sécurisés)
- 📱 Interface responsive Vue.js 3 (Tailwind CSS, thèmes Champagne)
- 🏷️ Système QR code par bouteille physique (tracking individuel)
- 🎨 **2 thèmes Champagne** : Clair (crème doré) et Sombre (brun/noir profond)
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
│   ├── src/styles/         # variables.css (thèmes Champagne)
│   ├── package.json        # Dépendances: Vue3, Tailwind, Leaflet, qrcode.vue
│   └── index.html          # Import Google Fonts "Beth Ellen"
├── backend/                # API FastAPI
│   ├── routers/            # Routeurs FastAPI (auth)
│   ├── services/           # Logique métier (pattern repository)
│   ├── alembic/            # Migrations Alembic (001→005)
│   ├── models.py           # Modèles SQLAlchemy
│   ├── schemas.py          # Schémas Pydantic
│   ├── main.py             # Routes API FastAPI
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
| `backend/services/*.py` | 6 services métier + consume_bottle_from_position |
| `backend/fonts/` | Polices TTF embarquées (Montserrat-Bold, NunitoSans-Regular/Bold) |
| `frontend/src/App.vue` | Layout principal (header "Pinaar" en Beth Ellen, navigation, modals) |
| `frontend/src/styles/variables.css` | Thèmes Champagne Clair + Sombre |
| `frontend/src/composables/useTheme.js` | Thème par défaut `champagne`, toggle champagne/champagne-dark |
| `frontend/src/router/index.js` | Routes SPA avec auth guards |
| `nginx.conf` | Reverse proxy Nginx |
| `entrypoint.sh` | Auto-setup: migrations, admin, uvicorn, nginx |
| `docker-compose.dev.yml` | Docker Compose dev local (ports 9080/9094) |

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
**Mécanisme de tracking physique** : `quantity` = stock logique total, chaque unité physique est un `PhysicalBottle` avec QR code unique. Le positionnement en cave déplace le `PhysicalBottle`, pas le `Bottle`.
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
- `DELETE /positions/{id}/bottle` - Retirer bouteille (libère position, garde en stock)
- `POST /positions/{id}/consume` - Consommer bouteille depuis position (historique) 🆕

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
'/map'           → MapView (Leaflet avec fitBounds auto)
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

### Theme System (Thèmes Champagne)

| Fichier | Rôle |
|---------|------|
| `tailwind.config.js` | Mapping `gh-*` → `var(--*)` (colors, shadows, radii, zIndex) |
| `src/styles/variables.css` | Définition des CSS custom properties pour chaque thème |
| `src/composables/useTheme.js` | Défaut `champagne`, toggle `champagne/champagne-dark`, persistance `localStorage` |
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

#### Thèmes disponibles (2 uniquement)
| Thème | `data-theme` | Description |
|-------|-------------|-------------|
| **Clair** (défaut) | — | `:root` — Crème champagne `#f5f3ee`, texte `#2d2926`, accent doré `#c5a265` |
| **Sombre** | `champagne-dark` | `#1a1814` fond brun/noir, texte `#e8e2d9`, accent doré `#c5a265` |

Le switcher de thème se trouve dans le **menu burger** de `App.vue`.

#### Phases de vin (couleurs pastels lisibles sur les deux thèmes)
| Phase | Clair | Sombre |
|-------|-------|--------|
| Jeunesse | `#3a6b52` (vert bouteille, visible sur fond clair) | `#cffd8e` (vert pastel) |
| Maturité | `#8ecafd` (bleu pastel) | `#8ecafd` (bleu pastel) |
| Apogée | `#fd8ea8` (rose pastel) | `#fd8ea8` (rose pastel) |
| Déclin | `#fdb38e` (orange pastel) | `#fdb38e` (orange pastel) |

#### Variables spéciales
| Variable | Clair | Sombre | Utilisation |
|----------|-------|--------|-------------|
| `--card-image-bg` | `#ffffff` | `#2e2820` | Fond des miniatures image dans BottleCard et BottleDetail |

### Principaux Composants
| Composant | Rôle |
|-----------|------|
| `BottleCard` | Carte vin dans liste (grid/list) — fond image blanc, fond info crème |
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

### MapView — Carte interactive
- **Leaflet.js** avec `fitBounds` auto : cadrage sur tous les marqueurs au chargement
- **Pane dédié** `markers-pane` (z-index 650) : les marqueurs restent visibles au zoom
- **FlyTo** fluide : animation `flyToBounds` et `flyTo` pour transitions douces
- **Bouton "Tout voir"** : recentre sur tous les marqueurs depuis la sidebar ou la carte
- **Géocodage Nominatim** : fallback pour régions inconnues (rate-limité 1.1s)

### Thème visuel (Champagne Elegant - défaut)
| Couleur | Hex | Utilisation |
|---------|-----|-------------|
| Background | `#f5f3ee` | Fond principal crème |
| Surface | `#ffffff` | Cards, modals |
| Border | `#e3dfd4` | Bordures taupe clair |
| Text | `#2d2926` | Texte principal (gris très chaud) |
| Text muted | `#b8b0a8` | Labels, secondaire |
| Accent | `#c5a265` | Boutons, liens, focus (doré champagne) |
| Success | `#3a6b52` | Boutons positifs (vert bouteille) |
| Danger | `#c44542` | Erreurs, suppression (rouge brique) |

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

### `108622a` - feat: add champagne themes, responsive UI fixes, map fitBounds, and backend consume endpoint
- **Thèmes** : Remplacement des 4 thèmes legacy par **2 thèmes Champagne** (Clair + Sombre)
- **Branding** : Titre "Pinaar" avec font Google **Beth Ellen** dans header + login
- **CardView** : Zone image en fond blanc (`--card-image-bg`), zone info en `--bg-primary`
- **Responsive** : Cellules cave agrandies, boutons +/- accessibles, filtres scrollables, images compactes
- **Map** : `fitBounds` automatique, pane markers au-dessus des tiles (fix zoom), bouton "Tout voir"
- **Backend** : Nouvel endpoint `POST /positions/{id}/consume` pour consommer depuis la cave
- **Divers** : `useTheme.js` key `pinarr-theme-v2`, phase "Jeunesse" lisible en clair `#3a6b52`

### `5875a84` - fix(qr-labels): inject frontend URL in single label + preserve X-Forwarded headers
### `870983e` - fix(ci): build frontend natively with BUILDPLATFORM for multi-arch
### `72ea1cd` - fix(qr-labels): auto frontend URL + bigger bold footer
### `8d48c6b` - fix(labels): increase font sizes for readability (year 30pt, name 20pt, phases 15pt, footer 15pt)
### `f583a6e` - feat: Ajout du système QR code par bouteille physique
- Création table `physical_bottles` (Alembic migration 003)
- Chaque bouteille physique a un QR code unique (8 chars)
- Génération par lot depuis la fiche vin
- Scan QR public sans authentification
- Tracking : acquisition, consommation, déplacement
- Séparation quantity (total) vs cellar_count (en cave)

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

### Derniers commits sur `main`
```
108622a feat: add champagne themes, responsive UI fixes, map fitBounds, and backend consume endpoint
5875a84 fix(qr-labels): inject frontend URL in single label + preserve X-Forwarded headers
870983e fix(ci): build frontend natively with BUILDPLATFORM for multi-arch
72ea1cd fix(qr-labels): auto frontend URL + bigger bold footer
8d48c6b fix(labels): increase font sizes for readability
f583a6e feat: Ajout du système QR code par bouteille physique
```

### Fichiers modifiés dans cette session (2026-05-03) — session initiale
- `frontend/src/styles/variables.css` — Thèmes Champagne Clair/Sombre, suppression des 4 legacy
- `frontend/src/composables/useTheme.js` — Défaut `champagne`, toggle 2 thèmes, key `pinarr-theme-v2`
- `frontend/src/App.vue` — Header "Pinaar" Beth Ellen, menu burger 2 thèmes (Clair/Sombre)
- `frontend/index.html` — Import Google Fonts "Beth Ellen", title "Pinaar"
- `frontend/src/components/WinePhaseBadge.vue` — Nettoyage thèmes legacy, phases pastel
- `frontend/src/components/WinePhaseTimeline.vue` — Variables `--phase-*` au lieu d'accents fixes
- `frontend/src/components/BottleCard.vue` — `--card-image-bg` pour fond image, responsive touch
- `frontend/src/components/BottleSidebar.vue` — `cellar_quantity`, `.slice().sort()`
- `frontend/src/views/MapView.vue` — `fitBounds`, pane markers, `invalidateSize`, ref mapContainer
- `frontend/src/views/BottleList.vue` — Filtres scrollables, phases variables CSS
- `frontend/src/views/BottleDetail.vue` — `--card-image-bg` zone image, tableau scrollable
- `frontend/src/views/CaveView.vue` — Cellules agrandies, icônes visibles
- `frontend/src/views/ScanResultView.vue` — Image compacte
- `frontend/src/views/LoginView.vue` — Titre "Pinaar" Beth Ellen
- `frontend/tailwind.config.js` — Ajout `gh-card-image`
- `backend/services/cave_service.py` — `consume_bottle_from_position()`
- `backend/services/__init__.py` — Export `consume_bottle_from_position`
- `backend/main.py` — Route `POST /positions/{position_id}/consume`
- `backend/services/bottle_service.py` — Fix `_sync_physical_bottles` mark consumed au lieu de delete

### Fixes post-session (non commit — prêts à push)
- `backend/services/cave_service.py` — **Issue #2** : Fix transaction SQLAlchemy `db.begin()` conflit dans `create_row()` → remplacé par `db.commit()` direct
- `frontend/src/views/BottleDetail.vue` — **Issue #1** : Fix routing cave `cave_name` → `cave_id` dans `goToCaveFromPhysicalBottle()`
- `docker-compose.yml` — Revert à `ghcr.io/jjllrrvvrr/pinarr:latest` (image prod)
- `context.md` — Mise à jour de l'état du projet

---

## 🔴 TODO Restant

### Bugs connus
- [ ] Déconnexion : "Quitter" dans App.vue ne fonctionne pas toujours
- [ ] Statistiques : `totalBottles` / `totalValue` ne sont pas rafraîchies en temps réel après updateQuantity
- [ ] CaveView drag & drop : `swap` non atomique côté backend (nécessite endpoint dédié)

### Améliorations planifiées
- [ ] Refonte `updateQuantity` dans App.vue pour créer/supprimer `PhysicalBottle` en temps réel
- [ ] Migration script init admin inline vers fichier séparé
- [ ] Endpoint `POST /positions/swap` atomique côté backend
- [ ] Vérifier scan physique mobile après changements de routing

---

## 🚨 Points d'attention critiques

1. **Auth** : Le middleware dans `main.py` protège tout sauf explicitement : `/auth/*`, `/`, `/uploads/*`, `/api/scan/*`, `/api/remove/*`
2. **QR Codes Publics** : `/api/scan/{qr_code}` et `/api/remove/{id}` sont les seules routes publiques pour les scanners mobiles. La route frontend SPA `/bottle/{qrCode}` est aussi publique (pas de `beforeEnter`).
3. **Positions vs Quantities** : `bottle.quantity` est l'autorité conceptuelle, `PhysicalBottle` est le tracking réel
4. **Upload** : Toutes les images sont converties en WebP 85%, max 1920px
5. **Migrations** : `alembic upgrade head` est l'unique point d'entrée pour le schéma. Plus de `create_db_tables()` au boot.
6. **Single User** : Le système est actuellement conçu pour un seul utilisateur admin (is_admin=True par défaut)
7. **Thèmes** : Seuls 2 thèmes existent (`champagne` et `champagne-dark`). Les thèmes legacy (`dark`, `light`, `red-wine`, `green-nature`) ont été supprimés du CSS et du menu.

---

## 🗄️ Système de Migrations (Alembic)

> **PRINCIPE** : Alembic est la seule source de vérité pour le schéma. Le `create_db_tables()` traditionnel est remplacé par un `db_bootstrap.py` intelligent.

### Procédure pour futures migrations
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

## 🔗 Ressources

- Repo GitHub : https://github.com/jjllrrvvrr/Pinarr
- README : `/README.md`
- Architecture Backend : `/backend/ARCHITECTURE.md`
- Screenshots : `/docs/screenshots/`

---

*Made with love for Pinarr lovers* 🍷