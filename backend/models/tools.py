from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime, date

# change string to ObjectId for mongoDB
def change_to_objectId(value):
    try:
        return ObjectId(str(value))
    except(InvalidId, TypeError):
        return None

def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except(TypeError, ValueError):
        return None

def validate_dates(check_in, check_out):
    if not check_in or not check_out:
        return 