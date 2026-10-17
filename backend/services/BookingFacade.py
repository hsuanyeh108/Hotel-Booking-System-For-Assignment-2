from PricingRuleFactory import PricingRuleFactory
from backend.models.RoomManager import room_manager
from backend.models.BookingManager import booking_manager




class BookingFacade:
    def __init__(self, room_manager, booking_manager):
        self._rooms = room_manager
        self._bookings = booking_manager

    def book_room(self, room_id, guest_name, guest_email, guest_phone, check_in, check_out, pricing_type="standard"):

        # check guest fill in their info
        if not guest_name or not guest_email or not guest_phone:
            return None, "Please fill in the completed booking information."

        #check dates
        error = booking_manager.validate_dates(check_in, check_out)
        if error:
            return None, error

        #search rooms
        room = room_manager.get_room_by_id(room_id)
        if not room:
            return None, "Room not found."

        #check conflict
        real_room_id = str(room["_id"])
        if room_manager.booking_conflict(real_room_id, check_in, check_out):
            return None, "This room is already booked."

        #count nights
        nights = booking_manager.count_nights(check_in, check_out)

        #Factory get particular price rate with price_type
        try:
            rule = PricingRuleFactory.get_rule(pricing_type)

        except ValueError as error:
            return None, str(error)
        total_price = round(rule.apply(room["price"], nights), 2)

        booking_data = {
            "room_id" : real_room_id,
            "room_type" : room["room_type"],
            "price" : room["price"], 
            "img" : room.get("img"),
            "guest_name" : guest_name.strip(),
            "guest_email" : guest_email.strip(),
            "guest_phone" : guest_phone.strip(),
            "check_in" : check_in,
            "check_out" : check_out,
            "nights" : nights,
            "pricing_type" : pricing_type,
            "total_price" : total_price,
        }
        booking_id = booking_manager.create_booking(booking_data)

        return booking_id, None


booking_facade = BookingFacade(room_manager, booking_manager)