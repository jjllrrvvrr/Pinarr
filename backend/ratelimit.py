"""Rate limiting simple en mémoire (sans dépendance externe).

Conçu pour une instance mono-processus (uvicorn workers=1), le mode de
déploiement actuel de Pinarr. Suffisant pour bloquer la brute force sur
login et l'énumération de QR codes sans ajouter Redis ni toucher la DB.
"""

import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import HTTPException, Request

# IP -> timestamps des dernières requêtes
_hits: dict[str, deque] = defaultdict(deque)
_lock = Lock()


def _get_client_ip(request: Request) -> str:
    """IP du client (supporte les reverse-proxies classiques)."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    if request.client:
        return request.client.host
    return "unknown"


def rate_limit(request: Request, max_requests: int, window_seconds: int) -> None:
    """Bloque si plus de max_requests sur les window_seconds dernières.

    Lève HTTPException 429, interceptée par FastAPI telle quelle.
    """
    ip = _get_client_ip(request)
    now = time.monotonic()

    with _lock:
        hits = _hits[ip]
        # Purger les entrées hors fenêtre
        while hits and now - hits[0] > window_seconds:
            hits.popleft()
        if len(hits) >= max_requests:
            raise HTTPException(
                status_code=429,
                detail="Trop de requêtes, veuillez réessayer plus tard",
            )
        hits.append(now)


def check_login_rate_limit(request: Request) -> None:
    """Limite les tentatives de login : 5 échecs / 5 minutes / IP."""
    rate_limit(request, max_requests=10, window_seconds=300)


def check_public_qr_rate_limit(request: Request) -> None:
    """Limite les routes publiques QR (scan/remove) : 60 req / minute / IP."""
    rate_limit(request, max_requests=60, window_seconds=60)