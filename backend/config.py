import os # read .env
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv() # load MONGO_URI=mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/ to env variable

MONGO_URI = os.getenv("MONGO_URI") # read .env if not return none
DB_NAME = os.getenv("DB_NAME", "HotelBookingSystemAs2")
if not MONGO_URI:
    raise RuntimeError("Setting failed or is not set. Please set the .env file.")


client = MongoClient(MONGO_URI)
db = client[DB_NAME]# for models import
