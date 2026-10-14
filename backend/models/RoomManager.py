import re
from backend.config import db
from backend.models.tools import change_to_objectId


rooms_collection = db["rooms"]
booking_collection = db["bookings"]

ACTIVE_STATUSES = ["Pending", "Confirmed" ]
DEFAULT_IMG = "img/Hotel Single Room.jpg"

DEFAULT_ROOMS = [
    {"room_type": "Standard Single Room", "price": 45.0, "description": "Free Wi-Fi, Single Bed, Air Conditioning", "img": "img/Hotel Single Room.jpg"},
    {"room_type": "Double Room", "price": 90.0, "description": "Free Wi-Fi, Queen Bed, Breakfast included, City View", "img": "img/Double Room.jpg"},
    {"room_type": "Executive Room", "price": 120.0, "description": "Free Wi-Fi, King Bed, Ocean View, Free Parking & Breakfast", "img": "img/Excutive Room.jpg"},
    {"room_type": "Standard Single Room", "price": 45.0, "description": "Free Wi-Fi, Single Bed, Garden View", "img": "img/Single Room2.jpg"},
    {"room_type": "Double Room", "price": 90.0, "description": "Free Wi-Fi, Double Bed, Work Desk", "img": "img/Double Room2.jpg"},
    {"room_type": "Executive Room", "price": 120.0, "description": "Free Wi-Fi, King Bed, Balcony, VIP Lounge Access", "img": "img/Excutive Room2.jpg"},
]



class RoomManager:
    def __init__(_rooms, _bookings):
        pass


# initalize data, if data is empty set 6 defaults rooms when application run 
    def set_defaults(self):
        if rooms_collection.count_documents({}) == 0:
            rooms_collection.insert_many([dict(r) for r in DEFAULT_ROOMS])
            print("Default rooms set into MongoDB")
        else:
            print(f"Rooms already exist: {rooms_collection.count_documents({})}")

# get all rooms
    def get_all_rooms(self): 
        return list(rooms_collection.find().sort("_id", 1))

# using id to search rooms
    def get_by_id(self, room_id):
        roomId = change_to_objectId(room_id)
        if roomId is None:
            return None
        return rooms_collection.find_one({"_id": roomId})
        

# 
    def get_availability(self, check_in, check_out, room_type):
        pass

# search only available rooms
    def get_available(self, check_in, check_out):
        pass

# check the room was booked by others
    def check_booking_conflict(self, room_id, check_in, check_out):
        pass

    def check_active_rooms_booking(self, room_id):
        pass

    def add_room(self, room_data):
        pass

    def update(self, room_id, update_data):
        pass

    def delete(self, room_id):
        pass









