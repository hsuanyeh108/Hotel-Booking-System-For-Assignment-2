from flask import Blueprint, request, jsonify

from backend.models.AdminManager import admin_manager
from backend.models.RoomManager import room_manager, DEFAULT_IMG
from backend.models.BookingManager import booking_manager
from backend.services.BookingFacade import booking_facade
from backend.services.TokenDecorator import AuthenticationTokenService, TokenDecorator
from backend.services.NoficationContract import NotificationContract

#name "api" bluewprint, add "/api" prefix
api_bp = Blueprint("api", __name__)

#Authetication Register
#Only accept POST
@api_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    #read the Json request, if format is wrong, return None or empty string
    name, email, password = data.get("name"), data.get("email"), data.get("password")
    if not all([name, email, password]):
        return jsonify({"message": "name, email and password are required"}), 400
    #Three fields, if any is empty, return 400
    if admin_manager.get_by_email(email):
        return jsonify({"message": "User already exists"}), 409
    #If the email is existed, return 409(conflict)

    admin_id = admin_manager.create(username=email, password=password, email=email, name=name)
    #Create an admin account, password will be hashed, get the new admin id

    return jsonify({"id": admin_id, "name": name, "email": email,
                     "token": AuthenticationTokenService.generate_token(admin_id)}), 201
    #return the account data, directly signature token(no need to login), 201 means created

#Authentication Login
@api_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    admin = admin_manager.verify_by_email(data.get("email"), data.get("password"))
    if not admin:
        return jsonify({"message": "Invalid email or password"}), 401
    #verify the email and password, if failed, return 401
    #no show which account or password is wrong, for not leak what account is existed
    return jsonify({
        "id": str(admin["_id"]),
        "name": admin.get("name"),
        "email": admin.get("email"),
        "token": AuthenticationTokenService.generate_token(str(admin["_id"])),
    }), 200    
    #If success, return 200
    #admin["_id"] is the ObjectId that MongoDB, cannot transfer to Json, so use string
    #token is the pass for the call of protect API

#Authentication Profile
@api_bp.route("/auth/profile", methods=["GET"])
@TokenDecorator #verify the Authrization : Bearer <token>, admin data will put in request.current_admin(directly use)
def profile():
    admin = request.current_admin
    return jsonify({"id": str(admin["_id"]), "name": admin.get("name"), "email": admin.get("email")}), 200
    #return current admin id, name, email(exclude password)

#Room Create
@api_bp.route("/rooms", methods=["POST"])
@TokenDecorator
def create_room():
    data = request.get_json(silent=True) or {}
    room_type, price = data.get("room_type"), data.get("price")

    if not room_type or price is None:
        return jsonify({"message": "room_type and price are required"}), 400
    #Room type and price are required, price is None, avoid 0 seen as no fill
    try:
        price = float(price)
    except (TypeError, ValueError):
        return jsonify({"message": "price must be a number"}), 400
    #price transfer to float, if failed, return 400
    room_data = {
        "room_type": room_type,
        "price": price,
        "description": data.get("description", ""),
        "img": data.get("img") or DEFAULT_IMG,
    }
    #Consist to dictionary, no fill using empty string, no image use default image
    room_id = room_manager.add(room_data)
    return jsonify({"id": room_id, **room_data}), 201   
    #write in database, return 201, get ID
    #**room_data means unpack the dictionary

#Room Update
@api_bp.route("/rooms/<room_id>", methods=["PUT"])
@TokenDecorator
def update_room_api(room_id):
    data = request.get_json(silent=True) or {}
    room = room_manager.get_by_id(room_id)
    if not room:
        return jsonify({"message": "Room not found"}), 404
    #room_id is the variable of the url, cannot find then return 404
    try:
        price = float(data.get("price", room.get("price")))
    except (TypeError, ValueError):
        return jsonify({"message": "price must be a number"}), 400
    #data.get("price, room.get("price")) means if request new price, use it, if not, use old price
    #update for part of data
    update_data = {
        "room_type": data.get("room_type", room.get("room_type")),
        "price": price,
        "description": data.get("description", room.get("description")),
        "img": data.get("img", room.get("img")),
    }
    room_manager.update(room_id, update_data)
    return jsonify({"id": room_id, **update_data}), 200
    #data.get("price, room.get("price")) means if request new price, use it, if not, use old price
    #update and return 200

#Room Delete
@api_bp.route("/rooms/<room_id>", methods=["DELETE"])
@TokenDecorator
def delete_room_api(room_id):
    if not room_manager.get_by_id(room_id):
        return jsonify({"message": "Room not found"}), 404
    if room_manager.has_active_booking(room_id):
        return jsonify({"message": "Cannot delete a room type with active bookings"}), 409
    #use room_id to find the room, if not found, return 404
    #If this room has active booking, cannot delete, return 409
    room_manager.delete(room_id)
    return jsonify({"message": "Room deleted"}), 200  
    #If pass, delete the room, return 200

#All Bookings
@api_bp.route("/bookings", methods=["GET"])
@TokenDecorator
def list_bookings():
    return jsonify([serialize_booking(b) for b in booking_manager.get_all()]), 200
#Get all bookings,use Json serialize booking (list comprehension) to consist back 
#need token, booking include name, email, phone

#Confirm Bookings
@api_bp.route("/bookings/<booking_id>/confirm", methods=["PUT"])
@TokenDecorator
def confirm_booking_api(booking_id):
    if not booking_manager.get_by_id(booking_id):
        return jsonify({"message": "Booking not found"}), 404
    #use booking_id to find the booking, if not found, return 404
    booking_facade.confirm_booking(booking_id)
    return jsonify(serialize_booking(booking_manager.get_by_id(booking_id))), 200
    #find then call facade(change status and send notification)
    #read again the booking latest status
    #compore to web, only "Pending" can be confirmed, this API no check, already cancelled bookings can also confirmed

#Admin Notification Settings(Singleton)
#Read Notification
@api_bp.route("/admin/notifications", methods=["GET"])
@TokenDecorator #The "/api" prefix has been added, should be "/api/admin/notifications"
def get_notifications():  #Check the token, if no will enter error, is success will get here
    return jsonify(NotificationContract().dict()), 200
    #Every time will call the same object(Singleton). copy the dictionary and transfer to Json

#Admin Notification Settings(Singleton)
#Update Notification
@api_bp.route("/admin/notifications", methods=["PUT"])
@TokenDecorator #same url, using method PUT, and check the token first
def update_notifications(): #If the format is wrong, will not return error, will return None
    data = request.get_json(silent=True) or {} #If None, represent as empty dictionary
    allowed_keys = {"email_enabled", "log_enabled", "sender_email"} #list the form that can be updated
    unknown_keys = set(data.keys()) - allowed_keys #data.keys() means the user return all field, minus the white list will be the unknown fields
    if unknown_keys: #If there is unknown fields, it will  return 400 and list the fields that are unknown
        return jsonify({"message": f"Unknown setting(s): {sorted(unknown_keys)}"}), 400

    config = NotificationContract() #Get the whole system shared setting object(Singleton)
    for key, value in data.items(): #Fill in the key and value in the setting
        config.set_setting(key, value)#set_setting will use the shared object, so next time when notification, it will use new setting
    return jsonify(config.dict()), 200

#Serialize Tools(For MongoDB ObjectId/datetime change to String, otherwise jsonify will return error)
def serialize_room(room):
    room = dict(room)
    room["_id"] = str(room["_id"])
    return room
#dict(room) means copy the dictionary(dont change the original data)
#Change ObjectId to String

def serialize_booking(booking):
    booking = dict(booking)
    booking["_id"] = str(booking["_id"])
    if "created_at" in booking:
        booking["created_at"] = booking["created_at"].isoformat()
    return booking
#booking process one more, build time is "datetime", change to ISO string, otherwise jsonify will return error
