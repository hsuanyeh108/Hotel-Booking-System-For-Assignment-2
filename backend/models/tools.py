from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime, date

# change string to ObjectId for mongoDB
def change_to_objectId(value):
    try:
        return ObjectId(str(value))
    except(InvalidId, TypeError):
        return None


def validate_dates(check_in, check_out):
    if not check_in or not check_out:
        return "Please select both Check-in and Check-out dates."
    start = parse_date(check_in)
    end = parse_date(check_out)
    if start is None or end is None:
        return "Invalid date format."
    if start < date.today():
        return "Check-in date cannot be in the past."
    if end <= start:
        return "Check-out date must be later than Check-in date."
    return None

def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except(TypeError, ValueError):
        return None

def count_nights(check_in, check_out):
    return (parse_date(check_out) - parse_date(check_in)).days