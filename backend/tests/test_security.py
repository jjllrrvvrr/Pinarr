"""Tests des guards anti-SSRF et du rate limiter."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_ssrf_private_ips_rejected():
    from services.upload_service import _validate_url_host
    from exceptions import InvalidUploadException

    bad_urls = [
        "http://192.168.1.1/img.jpg",
        "http://10.0.0.5/img.jpg",
        "http://172.16.0.1/img.jpg",
        "http://127.0.0.1/img.jpg",
        "http://169.254.169.254/meta-data",
        "http://[::1]/x.jpg",
        "http://localhost/img.jpg",
        "ftp://example.com/img.jpg",
    ]
    for url in bad_urls:
        try:
            _validate_url_host(url)
            assert False, f"URL non bloquée: {url}"
        except InvalidUploadException:
            pass


def test_ssrf_public_host_accepted():
    from services.upload_service import _validate_url_host

    _validate_url_host("http://example.com/img.jpg")


def test_ratelimit_blocks_after_threshold():
    from ratelimit import rate_limit
    from fastapi import HTTPException

    class FakeReq:
        class client:
            host = "203.0.113.9"
        headers = {}

    blocked = 0
    for _ in range(10):
        try:
            rate_limit(FakeReq(), max_requests=5, window_seconds=60)
        except HTTPException as e:
            assert e.status_code == 429
            blocked += 1
    assert blocked == 5


def test_ratelimit_per_ip():
    """La limite est par IP : une autre IP n'est pas affectée,
    la 6e requête de la même IP est bloquée."""
    from ratelimit import rate_limit
    from fastapi import HTTPException
    import pytest

    class FakeReq:
        class client:
            host = "198.51.100.7"
        headers = {}

    class OtherReq:
        class client:
            host = "198.51.100.8"
        headers = {}

    # 5 requêtes OK pour .7, 1 OK pour .8 (compteurs indépendants)
    for _ in range(5):
        rate_limit(FakeReq(), max_requests=5, window_seconds=60)
    rate_limit(OtherReq(), max_requests=5, window_seconds=60)  # pas de 429

    # La 6e requête de .7 est bloquée
    with pytest.raises(HTTPException) as exc_info:
        rate_limit(FakeReq(), max_requests=5, window_seconds=60)
    assert exc_info.value.status_code == 429