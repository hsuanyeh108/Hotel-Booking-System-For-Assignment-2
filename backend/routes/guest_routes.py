from flask import Blueprint, render_template, request, redirect, url_for, flash, abort

from backend.models.RoomManager import room_manager
from backend.models.BookingManager import booking_manager
from backend.models.tools import validate_dates


guest_bp = Blueprint("guest", __name__)


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