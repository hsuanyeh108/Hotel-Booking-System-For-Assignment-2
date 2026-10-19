#Functional Testing — Notification Center (Singleton Pattern)
#method: pytest tests/test_notification.py -v

from backend.services.NoficationContract import NotificationContract
from backend.services.NotificationService import NotificationService, get_recent_notifications

def setup_function():
    #Before each test, reset Singleton and notification log, to avoid pollute
    NotificationContract.reset_testing()
    
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
    result = NotificationService().status_change(booking, "Confirmed")
    assert set(result["sent_via"]) == {"email", "log"}
    assert len(get_recent_notifications()) == 2


def test_service_disabled_email_channel():
    NotificationContract().set_setting("email_enabled", False)
    booking = {"booking_no": 4, "guest_email": "g@test.com"}
    result = NotificationService().status_change(booking, "Cancelled by Guest")
    assert result["sent_via"] == ["log"]
    assert len(get_recent_notifications()) == 1


def test_service_disabled_log_channel():
    NotificationContract().set_setting("log_enabled", False)
    booking = {"booking_no": 5, "guest_email": "g@test.com"}
    result = NotificationService().status_change(booking, "Confirmed")
    assert result["sent_via"] == ["email"]
    assert len(get_recent_notifications()) == 1


# ---------- Through API Test（Same as Postman）----------

def test_api_get_notification_settings_requires_login(client):
    resp = client.get("/api/admin/notifications")
    assert resp.status_code == 401


def test_api_update_notification_settings(client, auth_headers):
    resp = client.put("/api/admin/notifications",
                      json={"email_enabled": False}, headers=auth_headers)
    assert resp.status_code == 200
    assert NotificationContract().get_setting("email_enabled") is False

def test_confirming_a_booking_triggers_a_notification(client, auth_headers):
    import backend.config as config
    from backend.services.BookingFacade import booking_facade

    room = config.db["rooms"].find_one()          # When apps runs, put in the default rooms
    booking_id, error = booking_facade.book_room(
        str(room["_id"]), "Guest", "g@test.com", "0400000000",
        "2026-12-01", "2026-12-03",
    )
    assert error is None, error                    # If booking fails, this will show the reason

    resp = client.put(f"/api/bookings/{booking_id}/confirm", headers=auth_headers)
    assert resp.status_code == 200

    assert len(get_recent_notifications()) == 2    # email + log sent one 
