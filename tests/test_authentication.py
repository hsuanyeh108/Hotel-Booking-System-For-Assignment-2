#Functional Testing - Admin authentication (AdminManager, JWT token service)
#Run: python -m pytest tests/test_auth.py -v

import os
import jwt
import pytest
from datetime import datetime, timedelta, timezone

from backend.models.AdminManager import admin_manager
from backend.services.TokenDecorator import AuthenticationTokenService


# ---------- AdminManager ----------
def test_create_admin_stores_hashed_password():
    admin_id = admin_manager.create("a@test.com", "secret123", email="a@test.com", name="A")
    stored = admin_manager.get_by_id(admin_id)
    assert stored["password"] != "secret123"  # password must not be stored in plain text


def test_verify_by_email_success_and_wrong_password():
    admin_manager.create("b@test.com", "secret123", email="b@test.com", name="B")
    assert admin_manager.verify_by_email("b@test.com", "secret123") is not None
    assert admin_manager.verify_by_email("b@test.com", "wrong") is None
    assert admin_manager.verify_by_email("nobody@test.com", "secret123") is None


def test_get_by_id_with_invalid_id_returns_none():
    assert admin_manager.get_by_id("not-an-object-id") is None


# ---------- AuthenticationTokenService ----------
def test_token_round_trip():
    token = AuthenticationTokenService.generate_token("abc123")
    assert AuthenticationTokenService.decode_token(token)["admin_id"] == "abc123"


def test_expired_token_is_rejected():
    expired = jwt.encode(
        {"admin_id": "x", "exp": datetime.now(timezone.utc) - timedelta(hours=1)},
        os.environ["SECRET_KEY"], algorithm="HS256")
    with pytest.raises(jwt.ExpiredSignatureError):
        AuthenticationTokenService.decode_token(expired)


def test_token_signed_with_wrong_key_is_rejected():
    forged = jwt.encode({"admin_id": "x"}, "another-key", algorithm="HS256")
    with pytest.raises(jwt.InvalidTokenError):
        AuthenticationTokenService.decode_token(forged)