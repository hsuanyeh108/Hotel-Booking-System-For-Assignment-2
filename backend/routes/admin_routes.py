from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
#Blueprint: routes group, render_template: HTML template, request: request data(form, method), redirect & url_for: link to another page, session: user login data, flash: message show on next page, abort: stop immediately and return 404

from backend.models.AdminManager import admin_manager
from backend.models.RoomManager import room_manager, DEFAULT_IMG
from backend.models.BookingManager import booking_manager
from backend.services.BookingFacade import booking_facade
from backend.services.LoginDecorator import LoginDecorator
from backend.services.NoficationContract import NotificationContract
from backend.services.NotificationService import get_recent_notifications
#import project's admin, rooms, bookings, booking facade, login decorator, notification contract, notification log

admin_bp = Blueprint("admin", __name__)#build a "admin" blueprint
#first parameter is route prefix, second parameter is blueprint name

#url (/admin/login) can use GET (show form) and POST(send form)
#Login
@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
    #If send the form, read email and password(strip the spaces), the second parameter "" is default value that are not exist
        admin = admin_manager.verify_by_email(email, password)
        #before call, firn the email admin and verify by password, return admin data
        if admin: #If success login
            session.clear() #Clear the session to avoid pollute and attacker
            session["admin_logged_in"] = True #This is the LoginDecorator check the status  
            session["admin_name"] = admin.get("name") or email #If no name, use email
            return redirect(url_for("admin.dashboard")) #Redirect to dashboard
        flash("Invalid email or password.", "error") #password wrong, show the error message
    return render_template("admin_login.html") #Return the login page,GET request is also this line, to show empty form


#Logout
@admin_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("admin.login"))
#Clear the session, flash logout message, redirect to login page

#Register Admin
@admin_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        if not name or not email or not password:
            flash("Name, email and password are required.", "error")
            return redirect(url_for("admin.register"))
        #read three fields(name, email, password), if any is empty, will show error and return register page
        if admin_manager.get_by_email(email):
            flash("This email is already registered.", "error")
            return redirect(url_for("admin.register"))
        #To check the email is existed or not, if existed, will show error and return register page
        admin_manager.create(username=email, password=password, email=email, name=name)
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("admin.login"))
    return render_template("admin_register.html")
    #create an account(username can use email), show success message and redirect to login page
    #GET will show the register form

#Admin Dashboard
@admin_bp.route("/dashboard")
@LoginDecorator #The two decorator's sequence is important, if have not login will redirect to login page
def dashboard():
    bookings = booking_manager.get_all_order()
    booking_count = 0
    for booking in bookings:
        if booking["status"] != "Cancelled by Guest":
            booking_count = booking_count +1
    room_count = len(room_manager.get_all_rooms())
    return render_template("admin_dashboard.html", booking_count=booking_count, room_count=room_count)
    #Get all the room and booking data, return the dashboard
    #use list comprehension to filter the "Cancelled by Guest" booking, calculate number and room number
    #Two parameters: booking count, room count to the dashboard

#Booking Management
@admin_bp.route("/bookings")
@LoginDecorator
def bookings():
    return render_template("admin_bookings.html", bookings=booking_manager.get_all_order())
#Get all bookings, return to dashboard to show

#Confirm Bookings
#<booking_id> is dynamic parameter, only accept POST (send form), avoid use change the url to change the status
@admin_bp.route("/bookings/<booking_id>/confirm", methods=["POST"])
@LoginDecorator
def confirm_booking(booking_id):
    booking = booking_manager.get_booking_by_id(booking_id)
    if not booking:
        abort(404)
        #Cannot find this booking, return 404 error
    if booking["status"] != "Pending":
        flash("Only pending bookings can be confirmed.", "error")
        #Only pending booking can be confirmed
    else:
        booking_facade.confirm_booking(booking_id)
        flash(f"Booking BK-{booking['booking_no']} confirmed.", "success")
    return redirect(url_for("admin.bookings"))  
    #call Fcade, can change the status and send notification at the same time, and redirect to manage list

#Cancel Bookings
#<booking_id> is dynamic parameter, only accept POST (send form), avoid use change the url to change the status
@admin_bp.route("/bookings/<booking_id>/cancel", methods=["POST"])
@LoginDecorator
def cancel_booking(booking_id):    
    booking = booking_manager.get_booking_by_id(booking_id)
    if not booking:
        abort(404)
        #Cannot find this booking, return 404 error
    if booking["status"] not in ("Pending", "Confirmed"):
        flash("This booking is already cancelled.", "error")
        #Only pending and confirmed booking can be cancelled, if already cancelled, then show message
    else:
        booking_facade.cancel_booking(booking_id, cancelled_by="Admin")
        flash(f"Booking BK-{booking['booking_no']} cancelled.", "success")
    return redirect(url_for("admin.bookings"))
    #call Fcade, can change the status and send notification at the same time, and redirect to manage list

#Notification Settings(Singleton)
#"/admin/notifications" is prefix of the url
#GET method is for open the page, POST method is press the send button 
@admin_bp.route("/notifications", methods=["GET", "POST"])
@LoginDecorator #Login check, if no login, will return flash message and redirect to login page
def notifications():
    config = NotificationContract()#Get the whole system shared setting object(Singleton)
    if request.method == "POST": #Whether is sending the form, if is, then operate the code, not only jump off to the render_template
        config.set_setting("email_enabled", request.form.get("email_enabled") == "on")
        #read the form field, if checkbox is checked, will send out, default string "on", if no then get will get None
        config.set_setting("log_enabled", request.form.get("log_enabled") == "on")
        #read the form field, if checkbox is checked, will send out, default string "on", if no then get will get None
        flash("Notification settings updated.", "success")
        #success, show the flash message
        return redirect(url_for("admin.notifications"))
        #after update, return to the same page(Post-Redirect-Get)

    return render_template(
        "admin_notifications.html", 
        settings=config.dict(),
        recent_log=get_recent_notifications(10),
    )
    #GET open the page, using admin_notifications.html, current settings return to html, decide checkbox use default or not
    #notification_log is NotificationService record list of the records that are sent, new is at the back 
    #reversed means take the latest to the front
    #use list because reversed return, should transfer back to list
    #(10) means take the first 10 records of notification

#Room Types Management
def room_types():
    room_type = request.form.get("room_type", "").strip()
    price_raw = request.form.get("price", "").strip()
    #read all room types and price, return to dashboard
    if not room_type or not price_raw:
        return None, "Room name and price are required."
    #If any of them in the form is empty, return None and message
    try:
        price = float(price_raw)
    except ValueError:
        return None, "Price must be a number, e.g. 150."
    #Price must be a number
    if price <= 0:
        return None, "Price must be greater than 0."
    #Price must be greater than 0
    img = request.form.get("img", "").strip()
    if not img:
        img = DEFAULT_IMG
    return {
        "room_type": room_type,
        "price": price,
        "description": request.form.get("description", "").strip(),
        "img": img,
    }, None 
    #Return the form data with room types, price, description and image

#Admin Manage Rooms
#If the user is not logged in, redirect to login
@admin_bp.route("/rooms")
@LoginDecorator
def manage_rooms():
    return render_template("admin_room_type_listing.html", rooms=room_manager.get_all_rooms())

#Admin Manage Rooms- Add new rooms
#If the user is not logged in, redirect to login
@admin_bp.route("/rooms/new", methods=["GET", "POST"])
@LoginDecorator
def new_room():
    if request.method== "POST":
        room_data, error = room_types()
        if error:
            flash(error, "error")
            return render_template("admin_room_type_form.html", room=request.form, is_edit=False), 400
        #GET show empty form, is_edit=False, POST show the form, have error show flash and store the content user fill in 
        room_manager.add_room(room_data)
        flash("Room type added.", "success")
        return redirect(url_for("admin.manage_rooms"))
    return render_template("admin_room_type_form.html", room={}, is_edit=False)
    #If no error, add room, show success message and redirect to manage rooms

#Admin Manage Rooms- Edit rooms
#If the user is not logged in, redirect to login
@admin_bp.route("/rooms/<room_id>/edit", methods=["GET", "POST"])
@LoginDecorator
def edit_room(room_id):
    room = room_manager.get_room_by_id(room_id)
    if not room:
        abort(404)
    #Cannot find this room, return 404 error
    if request.method == "POST":
        room_data, error = room_types()
        if error:
            flash(error, "error")
            return render_template("admin_room_type_form.html", room={**request.form, "_id": room["_id"]}, is_edit=True), 400
        #POST have error, let the form content to dictionary and put _id, let the model know which room to update
        room_manager.update(room_id, room_data)
        #success then update the room
        flash("Room type updated.", "success")
        return redirect(url_for("admin.manage_rooms"))
    return render_template("admin_room_type_form.html", room=room, is_edit=True)
    #If success, GET put the current room to the form

#Admin Manage Rooms- Delete rooms
#If the user is not logged in, redirect to login
@admin_bp.route("/rooms/<room_id>/delete", methods=["POST"])
@LoginDecorator
def delete_room_route(room_id):
    if not room_manager.get_room_by_id(room_id):
        abort(404)
    #Use room_id Cannot find this room, return 404 error    
    if room_manager.check_active_rooms_booking(room_id):
        flash("Cannot delete a room type with active bookings.", "error")
    #If this room has active booking, cannot delete, flash message
    else:
        room_manager.delete(room_id)
        flash("Room type deleted.", "success")
    return redirect(url_for("admin.manage_rooms"))
    #If no error, delete the room, flash message and redirect to manage rooms