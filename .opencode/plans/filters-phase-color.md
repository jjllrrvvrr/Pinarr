# PLAN : Ajout de filtres couleur et évolution sur la page d'accueil

## 📋 ANALYSE ACTUELLE

Le fichier `BottleList.vue` gère l'affichage des bouteilles avec :

### Filtres existants :
- **Cépage** → filtre par cépage
- **Région** → filtre par région  
- **Millésime** → filtre par année
- **Domaine** → filtre par domaine
- **Pays** → filtre par pays
- **Tag** → filtre par tag

### Filtres manquants demandés :
- **Couleur de vin** → rouge, blanc, rosé
- **Évolution** → Jeunesse, Maturité, Apogée, Déclin

---

## 🎨 NOUVEAUX FILTRES À AJOUTER

### 1. Filtre "Couleur"
**Valeurs possibles :**
- `RED`, `WHITE`, `ROSE`, `EFFERVESCENT`, `AUTRE`

**Source :** Champ `bottle.type` (ex: "Vin Rouge", "Vin Blanc", "Vin Rosé", "Champagne", "Crémant")

**UI :** Boutons rectangulaires :
```
[ Rouge ] [ Blanc ] [ Rosé ] [ Efferv. ] [ Autre ]
```

**Logique :** 
- Si sélectionné : filtre par couleur
- Click sur bouton actif = désélection

### 2. Filtre "Évolution" (Phases)
**Valeurs possibles :**
- `JEUNESSE`, `MATURITE`, `APOGEE`, `DECLIN`

**Source :** Calcul basé sur `currentYear` vs `jeunesse_end`, `maturite_end`, `apogee_end`

**UI :** Boutons rectangulaires :
```
[ Jeunesse ] [ Maturité ] [ Apogée ] [ Déclin ]
```

**Logique :**
- Si `null` ou aucune donnée → pas d'affichage (ou "Non défini")
- Si `year <= jeunesse_end` → Jeunesse
- Si `year <= maturite_end` → Maturité
- Si `year <= apogee_end` → Apogée
- Sinon → Déclin

---

## 📝 MODIFICATIONS NÉCESSAIRES

### Fichier : `frontend/src/views/BottleList.vue`

#### 1. Ajouter les nouveaux filtres à l'état (lignes ~158-165)
```javascript
const filters = ref({
  cepage: null,
  region: null,
  year: null,
  domaine: null,
  country: null,
  tag: null,
  color: null,      // NOUVEAU
  phase: null       // NOUVEAU
})
```

#### 2. Ajouter les boutons UI (avant ligne 81)
```vue
<div v-if="!showHistory && !searchQuery" class="mb-4 flex flex-wrap items-center gap-2">
  <!-- Filtre Couleur -->
  <div class="flex items-center gap-1">
    <span class="text-[#8b949e] text-xs">Couleur:</span>
    <button v-for="c of colors" :key="c.value" 
            @click="setFilter('color', c.value)"
            :class="['px-2 py-1 rounded-full text-xs border transition', 
                     filters.color === c.value ? c.activeClass : c.inactiveClass]">
      {{ c.label }}
    </button>
  </div>
  
  <!-- Filtre Évolution -->
  <div class="flex items-center gap-1">
    <span class="text-[#8b949e] text-xs">Évolution:</span>
    <button v-for="p of phases" :key="p.value"
            @click="setFilter('phase', p.value)"
            :class="['px-2 py-1 rounded-full text-xs border transition',
                     filters.phase === p.value ? p.activeClass : p.inactiveClass]">
      {{ p.label }}
    </button>
  </div>
</div>
```

#### 3. Ajouter les boutons "actifs" sous les filtres existants (lignes ~83-111)
```vue
<button v-if="filters.color" @click="clearFilter('color')" ...>
  Couleur: {{ getColorLabel(filters.color) }} ×
</button>
<button v-if="filters.phase" @click="clearFilter('phase')" ...>
  Évolution: {{ getPhaseLabel(filters.phase) }} ×
</button>
```

#### 4. Modifier `filteredBottles` computed (lignes ~224-261)
```javascript
const filteredBottles = computed(() => {
  let result = props.bottles
  
  // ... filtres existants ...
  
  // NOUVEAU : Filtre couleur
  if (filters.value.color) {
    const colorMap = {
      RED: ['Vin Rouge', 'Rouge'],
      WHITE: ['Vin Blanc', 'Blanc'],
      ROSE: ['Vin Rosé', 'Rosé'],
      EFFERVESCENT: ['Champagne', 'Crémant', 'Espumoso', 'Sparkling', 'Effervescent'],
      AUTRE: ['Autre', 'Liée de Pressins', 'Macis']
    }
    result = result.filter(b => 
      colorMap[filters.value.color]?.some(c => b.type?.includes(c))
    )
  }
  
  // NOUVEAU : Filtre évolution
  if (filters.value.phase) {
    const currentYear = new Date().getFullYear()
    result = result.filter(b => {
      if (!b.jeunesse_end && !b.maturite_end && !b.apogee_end) return false
      const jeunesseEnd = b.jeunesse_end || b.year + 1
      const maturiteEnd = b.maturite_end || b.year + 4
      const apogeeEnd = b.apogee_end || b.year + 9
      if (filters.value.phase === 'JEUNESSE') return currentYear <= jeunesseEnd
      if (filters.value.phase === 'MATURITE') return currentYear > jeunesseEnd && currentYear <= maturiteEnd
      if (filters.value.phase === 'APOGEE') return currentYear > maturiteEnd && currentYear <= apogeeEnd
      if (filters.value.phase === 'DECLIN') return currentYear > apogeeEnd
      return false
    })
  }
  
  // ... filtre recherche ...
  
  return result
})
```

#### 5. Ajouter constants pour les boutons
```javascript
const colors = [
  { value: 'RED', label: 'Rouge', activeClass: 'bg-[#f85149]/20 text-[#f85149] border-[#f85149]/30', inactiveClass: 'bg-[#21262d] text-[#8b949e] border-[#30363d] hover:text-white' },
  { value: 'WHITE', label: 'Blanc', activeClass: 'bg-[#58a6ff]/20 text-[#58a6ff] border-[#58a6ff]/30', inactiveClass: 'bg-[#21262d] text-[#8b949e] border-[#30363d] hover:text-white' },
  { value: 'ROSE', label: 'Rosé', activeClass: 'bg-[#db61a2]/20 text-[#db61a2] border-[#db61a2]/30', inactiveClass: 'bg-[#21262d] text-[#8b949e] border-[#30363d] hover:text-white' },
  { value: 'EFFERVESCENT', label: 'Efferv.', activeClass: 'bg-[#e3b341]/20 text-[#e3b341] border-[#e3b341]/30', inactiveClass: 'bg-[#21262d] text-[#8b949e] border-[#30363d] hover:text-white' },
  { value: 'AUTRE', label: 'Autre', activeClass: 'bg-[#a371f7]/20 text-[#a371f7] border-[#a371f7]/30', inactiveClass: 'bg-[#21262d] text-[#8b949e] border-[#30363d] hover:text-white' }
]

const phases = [
  { value: 'JEUNESSE', label: 'Jeunesse', activeClass: 'bg-[#58a6ff]/20 text-[#58a6ff] border-[#58a6ff]/30', inactiveClass: 'bg-[#21262d] text-[#8b949e] border-[#30363d] hover:text-white' },
  { value: 'MATURITE', label: 'Maturité', activeClass: 'bg-[#3fb950]/20 text-[#3fb950] border-[#3fb950]/30', inactiveClass: 'bg-[#21262d] text-[#8b949e] border-[#30363d] hover:text-white' },
  { value: 'APOGEE', label: 'Apogée', activeClass: 'bg-[#a371f7]/20 text-[#a371f7] border-[#a371f7]/30', inactiveClass: 'bg-[#21262d] text-[#8b949e] border-[#30363d] hover:text-white' },
  { value: 'DECLIN', label: 'Déclin', activeClass: 'bg-[#f85149]/20 text-[#f85149] border-[#f85149]/30', inactiveClass: 'bg-[#21262d] text-[#8b949e] border-[#30363d] hover:text-white' }
]

const updateFilters = () => {
  // Recalculate visibleBottles when filters change
}
```

#### 6. Fonctions helper
```javascript
const getColorLabel = (color) => {
  return colors.find(c => c.value === color)?.label || color
}
const getPhaseLabel = (phase) => {
  return phases.find(p => p.value === phase)?.label || phase
}
```

---

## 🎯 COMPORTEMENT SOUHAITÉ

### Exemple 1 : Filtre "Blanc" + "Maturité"
- Affiche **UNIQUEMENT** les vins blancs qui sont actuellement en phase Maturité
- Autres vins (rouge, rosé) et autres phases (jeunesse, apogée, déclin) sont **masqués**

### Exemple 2 : Filtre "Rouge" seul
- Affiche tous les vins rouges (quelle que soit leur phase)

### Exemple 3 : Pas de filtre
- Affiche tous les vins (comportement par défaut)

### Exemple 4 : Filtre "Maturité" seul
- Affiche tous les vins en phase Maturité (quelle que soit leur couleur)

---

## 📊 ORDRE D'AFFICHEMENT

```
┌─────────────────────────────────────┐
│ En cave (26)  |  Historique (2)   │
├─────────────────────────────────────┤
│ Filtres actifs:                   │
│ [Couleur: Blanc ×] [Évolution: Maturité ×] [Effacer tout] │
├─────────────────────────────────────┤
│ [Rouge] [Blanc] [Rosé] [Efferv.] [Autre]  │
│ [Jeunesse] [Maturité] [Apogée] [Déclin]   │
├─────────────────────────────────────┤
│ [Grille/Liste]  🔍 Rechercher...   │
├─────────────────────────────────────┤
│ [Bouteilles filtrées...]            │
└─────────────────────────────────────┘
```

---

## ❓ QUESTIONS

**1. Pour les vins sans données de phases :**
- [ ] Ne pas afficher dans le filtre "Évolution"
- [ ] Afficher "Non défini" avec un bouton gris
- [ ] Ne pas afficher de filtre évolution si aucune bouteille avec phases

**2. Couleur par défaut (si `bottle.type` est null/empty) :**
- [ ] Afficher "Non spécifié" dans le filtre couleur
- [ ] Ne pas afficher de filtre couleur si bouteille sans type

**3. Logique ET vs OU pour les filtres :**
- [x] **ET** (AND) - Actuellement demandé : "Blanc ET Maturité"
- OU (OR) - Afficher si BLANC ou MATURE

**4. Filtrer sur historique ?**
- [x] OUI (actuellement demandé)
- [ ] Non (filtrer seulement sur "En cave")

**5. Affichage des boutons :**
- [x] **Boutons actifs** : couleur de fond + bordure
- [ ] Badge juste à côté des filtres existants (pas de boutons supplémentaires)

---

## ✅ PROPOSITION RECOMMANDÉE

1. **Boutons rectangulaires** à côté des filtres existants (lignes ~84-111)
2. **Filtre ET** (AND) - "Blanc" + "Maturité" = blancs EN maturité
3. **Non-affichage** des filtres si aucune donnée dans les bouteilles
4. **Badge dans "Filtres actifs"** avec bouton × pour effacer

---

**Souhaitez-vous que je procède avec cette implémentation ?**
