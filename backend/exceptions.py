"""Exceptions métier personnalisées pour SudoWine."""

from fastapi import HTTPException


class SudoWineException(Exception):
    """Exception de base pour SudoWine."""

    pass


class BottleNotFoundException(SudoWineException):
    """Bouteille non trouvée."""

    pass


class CaveNotFoundException(SudoWineException):
    """Cave non trouvée."""

    pass


class ColumnNotFoundException(SudoWineException):
    """Colonne non trouvée."""

    pass


class RowNotFoundException(SudoWineException):
    """Rangée non trouvée."""

    pass


class PositionNotFoundException(SudoWineException):
    """Position non trouvée."""

    pass


class MaxQuantityReachedException(SudoWineException):
    """Quantité maximale atteinte."""

    pass


class InvalidUploadException(SudoWineException):
    """Upload invalide."""

    pass


def handle_sudowine_exception(exc: SudoWineException) -> HTTPException:
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
