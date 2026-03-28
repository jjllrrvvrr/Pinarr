# PLAN : Résolution du double fichier data/pinarr.db

## 📋 ÉTAT ACTUEL

### Structure locale
```
/Users/julienlrvr/Documents/Pinarr/data/
├── pinarr.db              ← 86KB, 28 bouteilles (BONNE BASE)
├── pinarr.db.bak          ← Sauvegarde
└── data/
    └── pinarr.db          ← 86KB, 28 bouteilles (DOUBLON)
```

### Structure dans le conteneur Docker
```
/app/data/
├── pinarr.db              ← 86KB, 28 bouteilles (BONNE BASE)
├── .gitkeep
└── data/
    └── pinarr.db          ← 86KB, 28 bouteilles (DOUBLON)
```

## 🔍 ANALYSE

### Database.py
```python
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pinarr.db")

# Adapter le chemin pour Docker si nécessaire
if DATABASE_URL.startswith("sqlite:///./"):
    db_path = DATABASE_URL.replace("sqlite:///./", "sqlite:////app/data/")
```

**Conclusion** : Le conteneur utilise **`/app/data/pinarr.db`**, pas `/app/data/data/pinarr.db`.

### docker-compose.yml
```yaml
volumes:
  - ./data:/app/data
```

**Conclusion** : Le dossier local `./data` est monté sur `/app/data` dans le conteneur.

## ✅ SOLUTION RECOMMANDÉE

### Étape 1 : Copier les données (si `data/data/pinarr.db` a des données uniques)
Si les deux fichiers ont 28 bouteilles (identiques), on peut **supprimer le dossier `/app/data/data`**.

### Étape 2 : Vérifier que le conteneur utilise le bon fichier
Le conteneur utilise `/app/data/pinarr.db` → **C'est correct !**

### Étape 3 : Nettoyer les doublons locaux
Supprimer `/Users/julienlrvr/Documents/Pinarr/data/data/pinarr.db`

### Étape 4 : Modifier `.gitignore` si nécessaire
Le `.gitignore` contient `/data/` qui ignore **tout le dossier data/**, y compris `data/data/`.

Pour permettre de versionner `data/data/.gitkeep`, il faut supprimer `/data/` du `.gitignore`.

## 📝 MODIFICATIONS À FAIRE

### Fichier 1 : `.gitignore`
**Supprimer** la ligne `/data/` et remplacer par :
```
/data/*.db
/data/*.sqlite
/data/*.sqlite3
```

### Fichier 2 : `.gitignore`
**Ajouter** pour permettre le versionnement :
```
!data/.gitkeep
!data/data/.gitkeep
```

## ❓ QUESTIONS

**1. Les deux fichiers pinarr.db (local et dans data/data) sont-ils identiques ?**
- Si OUI → Supprimer simplement `data/data/pinarr.db`
- Si NON → Fusionner les données avant de supprimer

**2. Préfères-tu :**
- [ ] A) Nettoyer les doublons (supprimer `data/data/`)
- [ ] B) Modifier `.gitignore` pour versionner correctement `data/data/`

**3. Le conteneur Docker utilise-t-il la bonne base (`/app/data/pinarr.db`) ?**
- Vérification : 28 bouteilles dans `/app/data/pinarr.db`
- Résultat : ✅ OUI, le conteneur utilise la bonne base

---

**Status :** Analyse terminée. En attente de décision pour implémentation.
