# Functional tests for booking
# FR-G2 (guest books a room), FR-G4 (pricing rules), NFR-03 (no double booking)

 
from datetime import date, timedelta
 
import pytest
 
 
def future(days):
    # always build dates from today, so these tests never become "past date" tests
    return (date.today() + timedelta(days=days)).isoformat()
 
 
@pytest.fixture
def room_id(app):
    # put one room (150 per night) straight into the test database
    with app.app_context():
        from backend.models.RoomManager import room_manager
        return room_manager.add_room({"room_type": "Test Room", "price": 150.0})
 
 
def booking_data(room_id, **changes):
    data = {
        "room_id": room_id,
        "guest_name": "Test Guest",
        "guest_email": "guest@test.com",
        "guest_phone": "0400000000",
        "check_in": future(30),
        "check_out": future(33),   # 3 nights
    }
    data.update(changes)
    return data
 
 
#FR-G2: Guest fill in forms to book rooms
 
def test_create_booking_success(client, room_id):
    resp = client.post("/api/bookings", json=booking_data(room_id))
    assert resp.status_code == 201
    assert resp.get_json()["total_price"] == 450   # 150 x 3, standard rule
 
 
def test_booking_missing_required_field(client, room_id):
    resp = client.post("/api/bookings", json=booking_data(room_id, guest_name=""))
    assert resp.status_code == 400
 
 
def test_booking_check_in_in_the_past(client, room_id):
    resp = client.post("/api/bookings", json=booking_data(room_id, check_in="2020-01-01", check_out="2020-01-03"))
    assert resp.status_code == 400
    assert "past" in resp.get_json()["message"]
 
 
def test_booking_check_out_before_check_in(client, room_id):
    resp = client.post("/api/bookings", json=booking_data(room_id, check_in=future(33), check_out=future(30)))
    assert resp.status_code == 400
 
 
def test_booking_invalid_date_format(client, room_id):
    resp = client.post("/api/bookings", json=booking_data(room_id, check_in="30/12/2027"))
    assert resp.status_code == 400
    assert resp.get_json()["message"] == "Invalid date format."
 
 
def test_booking_room_does_not_exist(client, app):
    resp = client.post("/api/bookings", json=booking_data("000000000000000000000000"))
    assert resp.status_code == 400
    assert resp.get_json()["message"] == "Room not found."
 
 
#FR-G4: Price calculation related to pricing rules
 
def test_list_pricing_rules(client):
    resp = client.get("/api/pricing/rules")
    assert resp.status_code == 200
    types = [rule["type"] for rule in resp.get_json()]
    assert types == ["standard", "weekend", "long_stay"]
 
 
def test_booking_with_unknown_pricing_rule(client, room_id):
    resp = client.post("/api/bookings", json=booking_data(room_id, pricing_type="vip"))
    assert resp.status_code == 400
    assert "Unknown pricing rule" in resp.get_json()["message"]
 
 
#NFR-03: the same room cannot be booked twice
 
def test_double_booking_same_room_is_rejected(client, room_id):
    first = client.post("/api/bookings", json=booking_data(room_id))
    assert first.status_code == 201
    second = client.post("/api/bookings", json=booking_data(room_id))
    assert second.status_code == 409
