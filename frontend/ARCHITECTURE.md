# Architecture Frontend Pinarr

## Structure du projet

```
frontend/src/
├── config.js                    # Configuration centralisée
├── main.js                     # Point d'entrée Vue.js
├── App.vue                     # Composant racine (simplifié)
├── router/
│   └── index.js                # Configuration Vue Router
├── services/                   # Couche d'accès API
│   ├── index.js               # Exports centralisés
│   ├── api.js                 # Client HTTP configuré
│   ├── bottleService.js       # Service bouteilles
│   ├── caveService.js         # Service caves/colonnes/rangées
│   └── uploadService.js       # Service uploads
├── composables/                # Logique réactive Vue
│   └── useBottles.js          # Gestion état bouteilles
├── components/                 # Composants réutilisables
│   ├── BottleCard.vue
│   └── BottlePreview.vue
└── views/                      # Pages/Vues
    ├── AddBottle.vue
    ├── BottleDetail.vue
    ├── BottleList.vue
    ├── CaveView.vue
    ├── MapView.vue
    └── RegionView.vue
```

## Principes

1. **Services**: Toute la logique API isolée
2. **Composables**: Gestion d'état réactive avec Vue 3 Composition API
3. **Configuration**: Centralisée dans config.js
4. **Pas de console.log en production**: Utiliser des gestionnaires d'erreurs

## Utilisation

### Dans un composant

```vue
<script setup>
import { useBottles } from '../composables/useBottles.js'

const { bottles, loading, totalBottles, deleteBottle } = useBottles()
</script>
```

### Service direct

```javascript
import BottleService from '../services/bottleService.js'

const bottle = await BottleService.getById(123)
```

## Configuration

Créer un fichier `.env` à la racine du frontend:

```
VITE_API_URL=http://localhost:8000
```
