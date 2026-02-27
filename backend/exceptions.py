"""Exceptions métier personnalisées pour Pinarr."""

from fastapi import HTTPException


class PinarrException(Exception):
    """Exception de base pour Pinarr."""

    pass


class BottleNotFoundException(PinarrException):
    """Bouteille non trouvée."""

    pass


class CaveNotFoundException(PinarrException):
    """Cave non trouvée."""

    pass


class ColumnNotFoundException(PinarrException):
    """Colonne non trouvée."""

    pass


class RowNotFoundException(PinarrException):
    """Rangée non trouvée."""

    pass


class PositionNotFoundException(PinarrException):
    """Position non trouvée."""

    pass


class MaxQuantityReachedException(PinarrException):
    """Quantité maximale atteinte."""

    pass


class InvalidUploadException(PinarrException):
    """Upload invalide."""

    pass


def handle_pinarr_exception(exc: PinarrException) -> HTTPException:
    """Convertit une exception métier en HTTPException."""
    status_map = {
        BottleNotFoundException: 404,
        CaveNotFoundException: 404,
        ColumnNotFoundException: 404,
        RowNotFoundException: 404,
        PositionNotFoundException: 404,
        MaxQuantityReachedException: 400,
        InvalidUploadException: 400,
    }
    status_code = status_map.get(type(exc), 500)
    return HTTPException(status_code=status_code, detail=str(exc))
