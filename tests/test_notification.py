#Functional Testing — Notification Center (Singleton Pattern)
#method: pytest tests/test_notification.py -v

from backend.services.NoficationContract import NotificationContract
from backend.services.NotificationService import NotificationService, get_recent_notifications

# ---------- Singleton Pattern ----------
def test_singleton_returns_the_same_instance():
    a = NotificationContract()
    b = NotificationContract()
    assert a is b  # Two calls take the same object, not two new objects.

def test_singleton_setting_change_is_visible_everywhere():
    a = NotificationContract()
    a.set_setting("email_enabled", False)

    b = NotificationContract()  # Another "look-alike" instance.
    assert b.get_setting("email_enabled") is False  # Because it's the same setting


def test_dict_returns_a_copy_not_the_internal_state():
    config = NotificationContract()
    snapshot = config.dict()
    snapshot["email_enabled"] = "tampered"
    # Change snapshot should not affect the internal state(encapsulation)
    assert config.get_setting("email_enabled") is True


# ---------- NotificationService：Accoding to Singleton setting decide what notification to send----------

def test_service_sends_via_both_channels_by_default():
    booking = {"booking_no": 3, "guest_email": "g@test.com"}
    result = NotificationService().notify_status_change(booking, "Confirmed")
    assert set(result["sent_via"]) == {"email", "log"}
    assert len(get_recent_notifications()) == 2


def test_service_disabled_email_channel():
    NotificationContract().set_setting("email_enabled", False)
    booking = {"booking_no": 4, "guest_email": "g@test.com"}
    result = NotificationService().notify_status_change(booking, "Cancelled by Guest")
    assert result["sent_via"] == ["log"]
    assert len(get_recent_notifications()) == 1


def test_service_disabled_log_channel():
    NotificationContract().set_setting("log_enabled", False)
    booking = {"booking_no": 5, "guest_email": "g@test.com"}
    result = NotificationService().notify_status_change(booking, "Confirmed")
    assert result["sent_via"] == ["email"]
    assert len(get_recent_notifications()) == 1


# ---------- Through API Test（Same as Postman）----------

def test_api_get_notification_settings_requires_login(client):
    resp = client.get("/api/admin/notification-settings")
    assert resp.status_code == 401


def test_api_update_notification_settings(client, app):
    with app.app_context():
        from backend.models.AdminManager import create_admin
        create_admin(username="n@test.com", password="pass1234", email="n@test.com", name="N")
    login_resp = client.post("/api/auth/login", json={"email": "n@test.com", "password": "pass1234"})
    token = login_resp.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.put("/api/admin/notification-settings", json={"email_enabled": False}, headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["email_enabled"] is False

    resp = client.put("/api/admin/notification-settings", json={"sms_enabled": True}, headers=headers)
    assert resp.status_code == 400  # sms_enabled are not allowed field


def test_confirming_a_booking_triggers_a_notification(client, app):
    with app.app_context():
        from backend.models.AdminManager import create_admin
        create_admin(username="c@test.com", password="pass1234", email="c@test.com", name="C")
    login_resp = client.post("/api/auth/login", json={"email": "c@test.com", "password": "pass1234"})
    token = login_resp.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    room_resp = client.post("/api/rooms", json={"room_type": "Notify Room", "price": 50.0}, headers=headers)
    room_id = room_resp.get_json()["id"]
    booking_resp = client.post("/api/bookings", json={
        "room_id": room_id, "guest_name": "G", "guest_email": "g@test.com",
        "guest_phone": "0400000000", "check_in": "2027-03-01", "check_out": "2027-03-02",
    })
    booking_id = booking_resp.get_json()["_id"]

    assert len(get_recent_notifications()) == 0  # Create bookings still don't trigger notifications
    client.put(f"/api/bookings/{booking_id}/confirm", headers=headers)
    assert len(get_recent_notifications()) == 2  # After Confirmed, email + log will sent out one 
