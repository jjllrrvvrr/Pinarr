# ANALYSE DU BUG : Badges de phase incorrects

## 📋 RÉCAPITULATIF

### Wines testés
| Nom | Year | jeunesse_end | maturite_end | apogee_end | Badge actuel |
|-----|------|--------------|--------------|------------|--------------|
| **Moscato d'Asti** | 2013 | NULL | NULL | NULL | **MATURITÉ** ❌ (devrait être DÉCLIN) |
| **Muralhas de Monção** | 2020 | NULL | NULL | 2025 | **DÉCLIN** ✅ |

## 🔍 ANALYSE

###Cas 1: Moscato d'Asti (2013)
- **jeunesse_end**: NULL
- **maturite_end**: NULL  
- **apogee_end**: NULL
- **Badge actuel**: MATURITÉ
- **Devrait être**: DÉCLIN (2013 + 10 = 2023, +5 = 2028, on est en 2026, donc à partir de 2028 = DÉCLIN)

### Cas 2: Muralhas de Monção (2020)
- **jeunesse_end**: NULL
- **maturite_end**: NULL
- **apogee_end**: 2025
- **Badge actuel**: DÉCLIN
- **Devrait être**: DÉCLIN (2020 + 1 = 2021, +3 = 2024, +5 = 2025, donc à partir de 2025 = DÉCLIN)

## 🔧 CAUSE PROBABLE

Le badge utilise les **défauts** quand les colonnes sont NULL :

```javascript
const jeunesseEnd = props.jeunesseEnd || props.vintageYear + 10
const maturiteEnd = props.maturiteEnd || props.vintageYear + 20 
const apogeeEnd = props.apogeeEnd || props.vintageYear + 30
```

**Pour Moscato (2013)**:
- jeunesseEnd = 2013 + 10 = **2023**
- maturiteEnd = 2013 + 20 = **2033**  
- apogeeEnd = 2013 + 30 = **2043**

**Logique de badge (année = 2026)**:
- 2026 <= 2023 ? NON
- 2026 <= 2033 ? OUI → **MATURITÉ** ❌

**Le problème**: Les valeurs par défaut ne correspondent pas à ce que l'utilisateur a défini.

## ✅ SOLUTIONS POUSSÉES

### Option 1: Pas de défauts (recommandé)
Si NULL, ne pas afficher le badge du tout, ou afficher "Non défini"

### Option 2: Utiliser le schéma exact
- jeunesse_end = vintage + 1 (défaut 1 an)
- maturite_end = vintage + 4 (défaut 3 ans après jeunesse)
- apogee_end = vintage + 9 (défaut 5 ans après maturité)
- Déclin = apogee_end + 5

### Option 3: Stocker les valeurs dans la base
Toujours stocker les 3 colonnes (ne pas laisser NULL)

## ❓ QUESTIONS

**1. Pour les vins sans données de phases :**
- [ ] Afficher le badge quand même avec défauts (actuel) ?
- [ ] Ne pas afficher le badge (pas de données) ?
- [ ] Afficher "Non défini" ?

**2. Pour les vins avec `apogee_end` mais pas `jeunesse_end/maturite_end` :**
- [ ] Calculer à partir de `apogee_end` (retour en arrière) ?
- [ ] Afficher DÉCLIN si `apogee_end <= year` ?

**3. Valeurs par défaut à utiliser ?**
- [ ] Actuel: +10, +20, +30 ans ?
- [ ] Nouveau: +1, +4, +9 ans (comme dans timeline) ?

---

**Status:** Bug identifié. En attente de réponse pour la solution appropriée
