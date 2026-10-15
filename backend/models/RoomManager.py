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
    def __init__(self, db):
        self._rooms = db["rooms"]
        self._bookings = db["bookings"] # check the room is available need bookings data


# initalize data, if data is empty set 6 defaults rooms when application run 
    def set_defaults(self):
        if rooms_collection.count_documents({}) == 0:
            rooms_to_insert = []
            for room in DEFAULT_ROOMS:
                rooms_to_insert.append(dict(room))# copy a room data to monogodb prevent compermise origin data
            rooms_collection.insert_many(rooms_to_insert)
            print("Default rooms set into MongoDB")
        else:
            print(f"Rooms already exist: {rooms_collection.count_documents({})}")

# get all rooms
    def get_all_rooms(self): 
        return list(rooms_collection.find().sort("_id", 1))# start form (older create id)

# using id to search rooms
    def get_room_by_id(self, room_id):
        roomId = change_to_objectId(room_id)
        if roomId is None:
            return None
        return rooms_collection.find_one({"_id": roomId})
        

    def get_booked_roomId(self, check_in, check_out):
        return set(booking_collection.distinct("room_id", {"status": {"$in": ACTIVE_STATUSES}, "check_in": {"$lt": check_out}, "check_out": {"$gt": check_in}}))


    def _roomType_filter(self, room_type):
        if room_type:
            return {f"room_type": {"$regex": re.escape(room_type), "$options": "i"}}
        return {}



# get all the avilabe rooms 
    def get_avaiable_rooms(self, check_in=None, check_out=None, room_type=None):
        rooms = list(rooms_collection.find(self._roomType_filter(room_type)).sort("_id", 1))
        booked = set()
        if check_in and check_out:
            booked = self.get_booked_roomId(check_in, check_out)
        for room in rooms:
            room["available"] = str(room["_id"]) not in booked
        return rooms
    
# search only available rooms
    def search_available_rooms(self, check_in, check_out, room_type=None):
        rooms = self.get_availabe_rooms(check_in, check_out, room_type)
        result = []
        for room in rooms:
            if room["available"]:
                result.append(room)
        return result

# check the room was booked by others
    def check_booking_conflict(self, room_id, check_in, check_out):
        conflictBooking = booking_collection.find_one({"room_id": str(room_id), "status": {"$in" : ACTIVE_STATUSES}, "check_in": {"$lt": check_out}, "check_out": {"$gt": check_in}})
        return conflictBooking


    def check_active_rooms_booking(self, room_id):
        return booking_collection.find_one({"room_id": str(room_id), "status": {"$in": ACTIVE_STATUSES}}) is not None



    def add_room(self, room_data):
        result = rooms_collection.insert_one(dict(room_data))
        return str(result.inserted_id)

    def update(self, room_id, update_data):
        roomId = change_to_objectId(room_id)
        if roomId is not None:
            return rooms_collection.update_one({"_id": roomId}, {"$set": update_data})

    def delete(self, room_id):
        roomId = change_to_objectId(room_id)
        if roomId is not None:
            return rooms_collection.delete_one({"_id" : roomId})









