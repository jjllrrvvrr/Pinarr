# PLAN DE CORRECTION : Erreur de migration base de données v0.3

## 🐛 RAPPORT D'ERRREUR

### Symptômes
- `sqlite3.OperationalError: no such column: bottles.jeunesse_end`
- `sqlite3.OperationalError: no such column: bottles.maturite_end`
- Base de données recréée vide au lieu de migrer

### Cause racine
1. Modèles SQLAlchemy mis à jour avec `jeunesse_end`, `maturite_end`, `apogee_end`
2. Aucune migration Alembic créée pour ajouter ces colonnes
3. Le fichier `002_add_phase_columns.py` vient d'être créé

---

## ✅ ÉTAT ACTUEL

### Fichier créé :
```
backend/alembic/versions/002_add_phase_columns.py ✅
```

**Contenu :**
```python
def upgrade():
    op.add_column('bottles', sa.Column('jeunesse_end', sa.Integer(), nullable=True))
    op.add_column('bottles', sa.Column('maturite_end', sa.Integer(), nullable=True))
    op.add_column('bottles', sa.Column('apogee_end', sa.Integer(), nullable=True))
```

---

## 🔧 ÉTAPES À RÉALISER

### 1️⃣ Commit de la migration
```bash
git add backend/alembic/versions/002_add_phase_columns.py
git commit -m "fix: add migration 002 for phase columns (jeunesse_end, maturite_end, apogee_end)"
```

### 2️⃣ Push sur GitHub
```bash
git push origin main
```

### 3️⃣ Recréer le tag v0.3
```bash
git tag -d v0.3
git push origin :refs/tags/v0.3
git tag v0.3
git push origin v0.3
```

### 4️⃣ Vérifier entrypoint.sh
Le fichier `entrypoint.sh` exécute déjà `alembic upgrade head` :
```bash
python3 -m alembic upgrade head
```

---

## ✅ CORRECTION EN VALEUR PROPOSÉE

1. **Migration créée** → `002_add_phase_columns.py`
2. **Commit + push** → Push la migration sur GitHub
3. **Tag recréé** → Tag v0.3 avec migration incluse
4. **Entrypoint** → Déjà configuré pour exécuter migrations

---

## 📋 CHECKLIST POUR L'USER

Après que vous ayez push et recréé le tag, l'utilisateur devra :

```bash
# Sur le serveur
docker-compose stop pinarr
docker-compose pull
docker-compose up -d
```

Alembic exécutera automatiquement la migration `002` qui ajoutera les colonnes manquantes.

---

## ⚠️ PROBLÈME CRITIQUE IDENTIFIÉ

**Le conteneur utilise une base de données créée par `create_db_tables()`** qui:
- Ne vérifie PAS la version d'Alembic
- Ne détecte PAS les migrations manquantes
- Recrée UNE NOUVELLE base si les colonnes attendues ne sont pas présentes

### SYMPTÔME:
```
WARNING: Database missing columns, recreating...
```

### RÉSOLUTION:
L'`entrypoint.sh` exécute `alembic upgrade head` → **ceci est correct** ✅

Mais le problème est que `create_db_tables()` est exécuté AVANT `alembic upgrade head` dans le setup Docker!

---

## 📝 MODIFICATIONS SUPPLÉMENTAIRES RECOMMANDÉES

### Modèle 1: Ignorer create_db_tables si alembic gère les migrations
Modifier `backend/main.py` pour ignorer `create_db_tables()` si les tables existent déjà.

### Modèle 2: Vérifier la version d'alembic avant create_db_tables
Vérifier `alembic_version` table avant de créer les tables.

---

**Souhaitez-vous que je prépare ces modifications supplémentaires pour éviter le problème à l'avenir ?**
