from flask import Blueprint, render_template, request, redirect, url_for, flash, abort

from backend.models.RoomManager import room_manager
from backend.models.BookingManager import booking_manager
from backend.models.tools import validate_dates
from services.BookingFacade import BookingFacade
from services.PricingRuleFactory import PricingRuleFactory


guest_bp = Blueprint("guest", __name__)

ACTIVE_STATUSES = ["Pending", "Confirmed"]

#Home and search
@guest_bp.route("/")
def home():
    check_in = request.args.get("check_in", "").strip()
    check_out = request.args.get("check_out", "").strip()
    query = request.args.get("query", "").strip()

    if check_in or check_out:
        error = validate_dates(check_in, check_out)
        if error:
            flash(error, "error")
            check_in = check_out = ""

    rooms = room_manager.get_avaliable_rooms(check_in or None, check_out or None, query or None)
    return render_template("search.html", rooms=rooms, check_in=check_in, check_out=check_out, query=query)


# book a room
@guest_bp.route("/book/<room_id>", methods=["GET", "POST"])
def book(room_id):
    room = booking_manager.get_booking_by_id(room_id)
    if not room:
        abort(404)

    pricing_rules = PricingRuleFactory.list_rule()

    if request.method == "POST":
        form = request.form
        booking_id, error = BookingFacade.book_room(
            room_id = room_id,
            guest_name = form.get("guest_name", ""),
            guest_email = form.get("guest_email", ""),
            guest_phone =form.get("guest_phone", ""),
            check_in = form.get("check_in", ""),
            check_out = form.get("check_out", ""),
            pricing_rules = form.get("pricing_rule", "")
        )
        if error:
            flash(error, "error")
            return render_template("booking_form.html", room=room, check_in = form.get("check_in", ""), check_out = form.get("check_out", ""), form=form, pricing_rules=pricing_rules), 400
        return redirect(url_for("guest.booking_success", booking_id=booking_id))

    return render_template(
        "booking_form.html", room=room, 
        check_in = request.args.get("check_in", ""),
        check_out = request.args.get("check_out", ""),
        form ={},pricing_rules=pricing_rules
    )

#booking success result
@guest_bp.route("/booking-success/<booking_id>")
def booking_success(booking_id):
    booking = booking_manager.get_booking_by_id(booking_id)
    if not booking:
        abort(404)
    return render_template("booking_success.html", booking=booking)


#check order(my_booking)
@guest_bp.route("/my-bookings", methods= ["GET", "POST"])
def my_bookings():
    booking = None
    searched = False
    if request.method == "POST":
        searched = True
        booking_no = request.form.get("booking_no", "")
        phone = request.form.get("guest_phone", "")
        if not booking_no.strip() or not phone.strip():
            flash("Please enter BOTH Booking ID and Phone Number to search!", "error")
            searched = False
        else:
            booking = booking_manager.get_booking_by_numAndPhone(booking_no, phone)
    return render_template("booking_list.html", booking=booking, searched=searched)


#cancell booking
@guest_bp.route("/cancel/<booking_id>", methods = ["POST"])
def cancel_booking(booking_id):
    booking = booking_manager.get_booking_by_id(booking_id)
    if not booking:
        abort(404)

    if booking["status"] not in ACTIVE_STATUSES:
        flash("This booking is already cancelled.", "error")
    else:
        cancel_booking(booking_id, cancelled_by="Guest")
        flash(f"Booking BK-{booking['booking_no']} has been cancelled.", "success")
    return redirect(url_for("guest.cancel"))