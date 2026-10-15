import os
from datetime import date

from flask import Flask, render_template, url_for
from RoomManager import RoomManager, DEFALUT_IMG

room_manager = RoomManager()
room_manager.set_defaults()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(FRONTEND_DIR, "templates"),
        static_folder=os.path.join(FRONTEND_DIR, "static"),
    )


    app.secret_key = os.getenv("", "")

    app.register_blueprint(guest.bp)
    app.register_blueprint(admin.bp, url_prefix="/")
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.template_filter("aud")
    def aud(value):
        try:
            number = float(value)
        except(TypeError, ValueError):
            return value
        if number == int(number):
            return f"A${number:,.0f}"
        else:
            return f"A${number:,.2f}"


    @app.template_filter("img_src")
    def img_src(path):
        path = path or DEFALUT_IMG
        if path.startswith("http://", "https://"):
            return path
        return url_for("static", filename=path.lstrip("/"))

    

    @app.template_filter("status_class")
    def status_class(status):
        if status == "Confirmed":
            return "status-confirmed"
        if status == "Pending":
            return "status-pending"
        return "status-cancelled"

    @app.context_processor
    def inject_today():
        return {"today": date.today().isoformat()}


    @app.errorhandler(404)
    def not_found(error):
        return render_template("error.html", message = 'Page not found.'), 404
    
    try:
        room_manager.set_defaults()
    except Exception as exc:
        print(f"Failed to initialize room: {exc}")


app = create_app()

if __name__ == "__main__":
    app.run(host="", port=int(os.getenv("PORT", )), debug=True)