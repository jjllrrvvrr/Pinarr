# Guide des Migrations de Base de Données

Ce document explique comment fonctionne le système de migrations de Pinarr.

## 🎯 Objectif

Les migrations permettent de mettre à jour le schéma de la base de données sans perdre les données utilisateur lors des mises à jour.

## 🔄 Fonctionnement Automatique

Quand un utilisateur met à jour Pinarr (via `git pull` puis `docker-compose up -d`) :

1. **Docker redémarre les containers**
2. **Alembic vérifie la version actuelle de la DB**
3. **Les migrations manquantes sont appliquées automatiquement**
4. **L'application démarre avec le nouveau schéma**

✅ **Les données utilisateur sont préservées**

## 📁 Structure des Fichiers

```
backend/
├── alembic/                  # Configuration Alembic
│   ├── env.py               # Configuration de l'environnement
│   ├── script.py.mako       # Template pour les nouvelles migrations
│   └── versions/            # Fichiers de migration
│       ├── .gitkeep
│       └── 001_initial_tables.py    # Migration initiale
│       └── 002_ajout_colonne_xyz.py # Futures migrations
├── alembic.ini             # Configuration principale
└── entrypoint.sh           # Exécute les migrations au démarrage
```

## 🛠️ Pour les Développeurs

### Créer une nouvelle migration

Quand vous modifiez les modèles (`models.py`), vous devez créer une migration :

```bash
# Se connecter au container backend
docker-compose exec backend bash

# Générer automatiquement la migration
cd /app
alembic revision --autogenerate -m "description des changements"

# Exemple : ajout d'une colonne 'vintage_year'
alembic revision --autogenerate -m "ajout colonne vintage_year"
```

### Vérifier la migration générée

Le fichier sera créé dans `backend/alembic/versions/`. **Vérifiez toujours son contenu !**

```python
"""ajout colonne vintage_year

Revision ID: 002
Revises: 001
Create Date: 2025-02-28 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'  # ← Référence à la migration précédente
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### Modification du schéma ###
    op.add_column('bottles', sa.Column('vintage_year', sa.Integer(), nullable=True))
    # ### Fin des modifications ###


def downgrade() -> None:
    # ### Annulation des modifications ###
    op.drop_column('bottles', 'vintage_year')
    # ### Fin des modifications ###
```

### Tester la migration

```bash
# Dans le container backend
cd /app

# Vérifier le statut
alembic current

# Tester la migration (sans l'appliquer définitivement)
alembic upgrade head --sql  # Affiche le SQL

# Appliquer la migration
alembic upgrade head

# En cas de problème, revenir en arrière
alembic downgrade -1  # Revient d'une version
```

### Commandes utiles

| Commande | Description |
|----------|-------------|
| `alembic current` | Voir la version actuelle de la DB |
| `alembic history` | Voir l'historique des migrations |
| `alembic upgrade head` | Appliquer toutes les migrations |
| `alembic downgrade -1` | Revenir à la version précédente |
| `alembic downgrade base` | Revenir à la version initiale |

## ⚠️ Bonnes Pratiques

### 1. Toujours vérifier les migrations générées

Alembic fait de son mieux, mais il peut se tromper. Vérifiez :
- Les colonnes ajoutées/supprimées
- Les contraintes (foreign keys, unique, etc.)
- Les valeurs par défaut

### 2. Ne pas modifier une migration déjà appliquée

Si une migration a déjà été appliquée chez les utilisateurs :
- ❌ Ne modifiez pas le fichier de migration
- ✅ Créez une nouvelle migration pour corriger

### 3. Tester les migrations sur une copie

Avant de pousser sur GitHub :
```bash
# Sauvegarder la DB
cp data/pinarr.db data/pinarr.db.backup

# Tester la migration
docker-compose down
docker-compose up -d

# Vérifier que tout fonctionne
# Si problème : restaurer la sauvegarde
```

### 4. Nommer clairement les migrations

- ✅ `"ajout colonne vintage_year"`
- ✅ `"creation table geocoded_regions"`
- ❌ `"fix"`
- ❌ `"update"`

## 🔒 Sécurité

- Les migrations sont **transactionnelles** : si une échoue, tout est annulé
- Les données sont **toujours préservées** (à moins de faire `DROP TABLE` explicitement)
- En cas de problème, on peut revenir en arrière avec `alembic downgrade`

## 🆘 Résolution de Problèmes

### "Database is locked"

Arrêtez l'application avant de faire des migrations manuellement :
```bash
docker-compose stop backend
# Faire les migrations...
docker-compose start backend
```

### Migration incompatible

Si une migration échoue :
1. Voir l'erreur : `docker-compose logs backend`
2. Corriger la migration
3. Réinitialiser : `alembic downgrade -1` puis `alembic upgrade head`

### Base de données corrompue

En dernier recours :
```bash
# Sauvegarder
cp data/pinarr.db data/pinarr.db.corrupted

# Supprimer et recréer
rm data/pinarr.db
docker-compose restart backend
# ⚠️ Perte de données !
```

## 📚 Ressources

- [Documentation Alembic](https://alembic.sqlalchemy.org/en/latest/)
- [SQLAlchemy Migrations](https://docs.sqlalchemy.org/en/14/orm/extensions/declarative/)
- Guide des opérations : [Alembic Operations](https://alembic.sqlalchemy.org/en/latest/ops.html)
