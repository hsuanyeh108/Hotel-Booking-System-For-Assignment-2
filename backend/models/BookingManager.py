import re
from backend.config import db
from backend.models.tools import change_to_objectId



class BookingManager:
    def __init__(self):
        pass

    def create_booking_number():
        pass

    def create(booking_data):
        pass

    def get_by_id(booking_id):
        pass

# guest check his own order
    def check_order(booking_num, phone):
        pass


    def get_guest_data(email, phone):
        pass

    def get_all_order():
        pass

# update data status
    def update_status(booking_id, status):
        pass




booking_manager = BookingManager(db)
