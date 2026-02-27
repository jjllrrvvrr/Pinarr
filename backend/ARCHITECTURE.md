# Architecture Backend Pinarr

## Vue d'ensemble

Le backend a été refactorisé selon une architecture en couches propre et maintenable.

## Structure du projet

```
backend/
├── config.py              # Configuration centralisée
├── database.py            # Configuration SQLAlchemy
├── dependencies.py        # Dépendances FastAPI réutilisables
├── exceptions.py          # Exceptions métier personnalisées
├── main.py               # Point d'entrée FastAPI (routes uniquement)
├── models.py             # Modèles SQLAlchemy
├── schemas.py            # Schémas Pydantic
└── services/             # Couche métier
    ├── __init__.py
    ├── bottle_service.py # Logique bouteilles
    ├── cave_service.py   # Logique caves/colonnes/rangées
    ├── upload_service.py # Uploads sécurisés
    └── geo_service.py    # Géocodage
```

## Principes suivis

1. **Single Responsibility Principle**: Chaque service a une responsabilité unique
2. **DRY (Don't Repeat Yourself)**: Factorisation du code dupliqué
3. **Configuration centralisée**: Tout dans config.py
4. **Gestion d'erreurs propre**: Exceptions métier personnalisées
5. **Sécurité renforcée**: Uploads avec validation complète

## Optimisations

- Requêtes SQL optimisées avec `joinedload` (évite N+1 queries)
- Validation MIME type + extension pour les uploads
- Limite de taille fichier configurable
- Pagination prête à être implémentée

## Pour démarrer

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
