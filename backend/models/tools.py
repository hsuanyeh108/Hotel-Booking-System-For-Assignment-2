from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime, date

# change string to ObjectId for mongoDB
def change_to_objectId(value):
    try:
        return ObjectId(str(value))
    except(InvalidId, TypeError):
        return None


