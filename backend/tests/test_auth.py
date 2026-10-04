"""Tests auth : hash bcrypt, tokens JWT, cycle login/logout."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_password_hash_roundtrip():
    from auth import hash_password, verify_password

    hashed = hash_password("monMotDePasse123")
    assert hashed != "monMotDePasse123"
    assert verify_password("monMotDePasse123", hashed)
    assert not verify_password("mauvais", hashed)


def test_jwt_token_roundtrip():
    from auth import create_access_token, decode_token

    token = create_access_token({"sub": "admin", "user_id": 1})
    payload = decode_token(token)
    assert payload["sub"] == "admin"
    assert payload["user_id"] == 1


def test_jwt_expired_token():
    from datetime import timedelta
    from auth import create_access_token, decode_token

    token = create_access_token(
        {"sub": "admin"}, expires_delta=timedelta(seconds=-10)
    )
    assert decode_token(token) is None


def test_jwt_invalid_token():
    from auth import decode_token

    assert decode_token("pas.un.token") is None


def test_login_flow_with_db(db):
    """Création user + vérification du lookup (comme /auth/login)."""
    from auth import hash_password
    from database import SessionLocal  # noqa: F401 - import implicite via conftest
    from models import User
    from sqlalchemy import text

    db.add(
        User(
            username="pytest_user",
            password_hash=hash_password("secret123"),
            is_admin=True,
        )
    )
    db.commit()

    result = db.execute(
        text("SELECT id, username, password_hash FROM users WHERE username = :u"),
        {"u": "pytest_user"},
    ).fetchone()
    assert result is not None

    from auth import verify_password

    assert verify_password("secret123", result[2])