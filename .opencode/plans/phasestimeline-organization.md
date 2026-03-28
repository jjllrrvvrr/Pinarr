# PLAN FINALISÉ : Organisation Gestion & Évaluation

## 📋 ÉTAT ACTUEL (lignes 230-367)

```
Gestion & Évaluation
├─ Position dans la cave (4 colonnes)
├─ Grille:
│  ├─ Quantité (col 1)
│  ├─ Prix (col 2)
│  └─ Phases (col 3 - 25% largeur)
├─ Note
├─ Tags
└─ Lien externe
```

---

## ✅ STRUCTURE FINALE DEMANDÉE

### grille principale (3 colonnes)
```
┌────────────────────────────────────────────────────────────┐
│ Quantité │ Prix │ Phases de développement (100%largeur)  │
└────────────────────────────────────────────────────────────┘

Note (à côté du Prix)     │  Phases (ligne complète)
└───────────────────┐     │  ┌─────────────────────────────────┐
│                 │     │  │                                 │
└───────────────────┘     │  │  [Timeline complète]            │
                          │  │                                 │
Note à côté du Prix       │  └─────────────────────────────────┘
└───────────────────────────────────────────────────────────────┘

Tags │ Lien externe
└───────────────────────┘
```

### Organisation réelle finales
```
┌──────────────────────────────────────────────────┐
│ ⏱ Gestion & Évaluation                          │
├──────────────────────────────────────────────────┤
│ 📍 Position dans la cave                        │
│ [Cave][Col][Etag][Pos]                          │
│ ────────────────────────────────────────────   │
│ [Quantité] │ [Prix] │ [Note]                 │
│ ────────────────────────────────────────────   │
│ ⏱ Phases de développement                      │
│ [Timeline complète 100%]                        │
│ ────────────────────────────────────────────   │
│ 🏷 Tags  │ 🔗 Lien externe                      │
└──────────────────────────────────────────────────┘
```

---

## 🔧 MODIFICATIONS À FAIRE

### Dans `/frontend/src/views/AddBottle.vue`

**Lignes 270-316** (grille actuelle Quantité | Prix | Phases)

```
<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
  <!-- Quantité -->
  <div>...</div>
  
  <!-- Prix & Note -->
  <div class="grid grid-cols-2 gap-3">
    <div>Prix</div>
    <div>Note</div>
  </div>
  
  <!-- Phases -->
  <div class="md:col-span-1">Timeline</div>
</div>
```

**Ligne 318-365** (Note, Tags, Lien)

```
<div class="grid grid-cols-2 gap-4">
  <!-- Tags -->
  <div>...</div>
  
  <!-- Lien externe -->
  <div>...</div>
</div>
```

---

## 📊 RÉSULTAT FINAL

| Élément | Colonne | Largeur | Hauteur |
|---------|---------|---------|---------|
| Position | - | 100% | 3 lignes |
| Quantité | 1/3 | 33% | auto |
| Prix | 2/3 | 33% | auto |
| Note | 3/3 | 33% | auto |
| Phases | - | 100% | 60px |
| Tags | 1/2 | 50% | auto |
| Lien | 2/2 | 50% | auto |

---

## ✅ VALIDATION

1. ✅ Phases de développement sur **ligne complète**
2. ✅ Note à côté du **Prix**
3. ✅ Tags et Lien sur **même ligne** (2 colonnes)

**Status :** Plan finalisé, prêt pour implémentation
