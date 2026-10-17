import re
from datetime import datetime, date, timezone
from pymongo import ReturnDocument
from backend.config import db
from models.tools import change_to_objectId
from models.RoomManager import room_manager



bookings_collection = db["bookings"]
counters_collection = db["counters"]



class BookingManager:
    def __init__(self, db):
        self._bookings = db["bookings"]
        self._counters = db["counters"]

    def parse_date(self, value):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except(TypeError, ValueError):
            return None

        
    def validate_dates(self, check_in, check_out):
        if not check_in or not check_out:
            return "Please select both Check-in and Check-out dates."
        
        start = self.parse_date(check_in)
        end = self.parse_date(check_out)

        if start is None or end is None:
            return "Invalid date format."
        if start < date.today():
            return "Check-in date cannot be in the past."
        if end <= start:
            return "Check-out date must be later than Check-in date."
        return None


    def count_nights(self, check_in, check_out):
        return (self.parse_date(check_out) - self.parse_date(check_in)).days
    

    def _create_next_booking_number(self,):
        doc = counters_collection.find_one_and_update({"_id": "bookings"}, {"$inc": {"seq": 1}}, uspert=True, return_document=ReturnDocument.AFTER)
        return doc["seq"]
    

    def create_booking(self, booking_data):
        booking_data = dict(booking_data)
        booking_data["booking_no"] = self._create_next_booking_number()
        booking_data["status"] = "Pending"
        booking_data["create_at"] = datetime.now(timezone.utc)
        result = bookings_collection.insert_one(booking_data)
        return str(result.inserted_id)


    def book_room(self, room_id, guest_name, guest_email, guest_phone, check_in, check_out):
        
        if not all([guest_name, guest_email, guest_phone, check_in, check_out]):
            return None, "Please fill in the complete booking information."

        error = self.validate_dates(check_in, check_out)
        if error:
            return None, error

        room = room_manager.get_room_by_id(room_id)
        if not room:
            return None, "Room not found. Please check your order information again."

        if room_manager.booking_conflict(str(room["_id"]), check_in, check_out):
            return None, "This room is already booked."



        nights = self.count_nights(self, check_in,check_out)
        total_price = round(room["price"] * nights, 2)
        booking_id = self.create_booking(
            {
                "room_id": str(room_id),
                "room_type": room["room_type"],
                "price": room["price"],
                "img": room.get("img"),
                "guest_name": guest_name.strip(),
                "guest_email": guest_email.strip(),
                "guest_phone": guest_phone.strip(),
                "check_in": check_in,
                "check_out": check_out,
                "nights": nights,
                "total_price": total_price,

            })
        return booking_id, None

    

    def get_booking_by_id(self, booking_id):
        id = change_to_objectId(booking_id)
        if id is None:
            return None
        return bookings_collection.find_one({"_id": id})

    

# guest check his own order
    def get_booking_by_numAndPhone(self, booking_no, phone):
        cleaned_input = str(booking_no).strip().upper().replace("BK-", "")
        if not cleaned_input.isdigit():
            return None
        return bookings_collection.find_one({"booking_no": int(cleaned_input), "guest_phone": str(phone).strip(),})

    

    def get_guest_data(self, email, phone):
        return list(bookings_collection.find({"guest_email": email, "guest_phone": phone}))
    

    def get_all_order(self):
        return list(bookings_collection.find().sort("booking_no", 1))


# update data status
    def update_status(self, booking_id, new_status):
        id = change_to_objectId(booking_id)
        if id is None:
            return bookings_collection.update_one({"_id": id}, {"$set": {"status": new_status}})


    def cancel_booking(self, booking_id, cancelled_by="Guest"):
        new_status = "Cancelled by Guest"
        if cancelled_by == "Guest":
            self.update_status(booking_id, new_status)
        else:
            "Cancelled by Admin."




booking_manager = BookingManager(db)
