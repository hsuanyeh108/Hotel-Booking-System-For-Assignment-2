#Functional Testing - Admin REST API (auth, room management, notification settings)
#Uses the Flask test_client to call the API, same endpoints Postman calls.
#Run: python -m pytest tests/test_admin_api.py -v

from backend.config import db

NEW_ROOM = {"room_type": "Test Suite", "price": 150, "description": "demo"}


# ---------- Authentication ----------
def test_register_success(client):
    resp = client.post("/api/auth/register", json={"name": "A", "email": "a@test.com", "password": "pass1234"})
    assert resp.status_code == 201
    assert "token" in resp.get_json()


def test_register_missing_field_returns_400(client):
    resp = client.post("/api/auth/register", json={"email": "a@test.com"})
    assert resp.status_code == 400


def test_register_duplicate_email_returns_409(client):
    body = {"name": "A", "email": "a@test.com", "password": "pass1234"}
    client.post("/api/auth/register", json=body)
    assert client.post("/api/auth/register", json=body).status_code == 409


def test_login_success_returns_token(client):
    client.post("/api/auth/register", json={"name": "A", "email": "a@test.com", "password": "pass1234"})
    resp = client.post("/api/auth/login", json={"email": "a@test.com", "password": "pass1234"})
    assert resp.status_code == 200
    assert resp.get_json()["token"]


def test_login_wrong_password_returns_401(client):
    client.post("/api/auth/register", json={"name": "A", "email": "a@test.com", "password": "pass1234"})
    resp = client.post("/api/auth/login", json={"email": "a@test.com", "password": "wrong"})
    assert resp.status_code == 401


def test_profile_with_token(client, auth_headers):
    resp = client.get("/api/auth/profile", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["email"] == "admin@test.com"


def test_profile_without_token_returns_401(client):
    assert client.get("/api/auth/profile").status_code == 401


def test_profile_with_invalid_token_returns_401(client):
    resp = client.get("/api/auth/profile", headers={"Authorization": "Bearer not.a.token"})
    assert resp.status_code == 401


# ---------- Room management ----------
def test_create_room_success(client, auth_headers):
    resp = client.post("/api/rooms", json=NEW_ROOM, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.get_json()["price"] == 150.0


def test_create_room_requires_token(client):
    assert client.post("/api/rooms", json=NEW_ROOM).status_code == 401


def test_create_room_missing_price_returns_400(client, auth_headers):
    resp = client.post("/api/rooms", json={"room_type": "No Price"}, headers=auth_headers)
    assert resp.status_code == 400


def test_create_room_non_numeric_price_returns_400(client, auth_headers):
    resp = client.post("/api/rooms", json={"room_type": "X", "price": "abc"}, headers=auth_headers)
    assert resp.status_code == 400


def test_update_room_success(client, auth_headers):
    room_id = client.post("/api/rooms", json=NEW_ROOM, headers=auth_headers).get_json()["id"]
    resp = client.put(f"/api/rooms/{room_id}", json={"price": 99}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["price"] == 99.0
    assert resp.get_json()["room_type"] == "Test Suite"  # fields not sent keep their old value


def test_update_room_not_found_returns_404(client, auth_headers):
    resp = client.put("/api/rooms/000000000000000000000000", json={"price": 1}, headers=auth_headers)
    assert resp.status_code == 404


def test_delete_room_success_then_404(client, auth_headers):
    room_id = client.post("/api/rooms", json=NEW_ROOM, headers=auth_headers).get_json()["id"]
    assert client.delete(f"/api/rooms/{room_id}", headers=auth_headers).status_code == 200
    assert client.delete(f"/api/rooms/{room_id}", headers=auth_headers).status_code == 404


def test_delete_room_without_token_returns_401(client):
    assert client.delete("/api/rooms/000000000000000000000000").status_code == 401


def test_delete_room_with_active_booking_returns_409(client, auth_headers):
    room_id = client.post("/api/rooms", json=NEW_ROOM, headers=auth_headers).get_json()["id"]
    db["bookings"].insert_one({"room_id": room_id, "status": "Confirmed",
                               "check_in": "2027-01-01", "check_out": "2027-01-03"})
    assert client.delete(f"/api/rooms/{room_id}", headers=auth_headers).status_code == 409


# ---------- Notification settings (Singleton) ----------
def test_notifications_get_requires_token(client):
    assert client.get("/api/admin/notifications").status_code == 401


def test_notifications_get_returns_defaults(client, auth_headers):
    resp = client.get("/api/admin/notifications", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["email_enabled"] is True


def test_notifications_update_persists_in_singleton(client, auth_headers):
    resp = client.put("/api/admin/notifications", json={"email_enabled": False}, headers=auth_headers)
    assert resp.status_code == 200 and resp.get_json()["email_enabled"] is False
    # GET again to confirm the setting was kept (same Singleton)
    again = client.get("/api/admin/notifications", headers=auth_headers)
    assert again.get_json()["email_enabled"] is False


def test_notifications_update_unknown_field_returns_400(client, auth_headers):
    resp = client.put("/api/admin/notifications", json={"sms_enabled": True}, headers=auth_headers)
    assert resp.status_code == 400


def test_bookings_list_requires_token(client):
    assert client.get("/api/bookings").status_code == 401