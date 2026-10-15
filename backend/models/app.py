import os #using for reading environment variables
from datetime import date #For generate today's date

from flask import Flask, render_template, url_for
#import flask for the whole system to use, render_template for 404 page, url_for for consist the image link
from backend.models.RoomManager import RoomManager, DEFAULT_IMG

room_manager = RoomManager()
#room_manager.set_defaults()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(FRONTEND_DIR, "templates"),
        static_folder=os.path.join(FRONTEND_DIR, "static"),
    )


    app.secret_key = os.getenv("SECRET_KEY")

    #app.register_blueprint(guest_bp)
    #app.register_blueprint(admin_bp, url_prefix="/admin")
    #The router is a box for collect different routes, add the prefix /admin at the front
    #app.register_blueprint(api_bp, url_prefix="/api")

    @app.template_filter("aud")
    def aud(value): #Format aud filter, ex: 45.0 to A$45 ; 99.5 to A$99.50
        try:
            number = float(value)
        except(TypeError, ValueError):
            return value
        if number == int(number):
            return f"A${number:,.0f}"
        else:
            return f"A${number:,.2f}"
        #If the value is an integer, then it will not have a decimal point

    @app.template_filter("img_src")
    def img_src(path): #Database store 'img/xxx.jpg', transfer to /static/img/xxx.jpg, if is http link then use directly
        path = path or DEFAULT_IMG #If the path is None, then use the default image
        if path.startswith(("http://", "https://")):
            return path
        return url_for("static", filename=path.lstrip("/"))

    

    @app.template_filter("status_class")
    def status_class(status): 
        #Jinja filter-- status_class, transfer status to CSS class(Confirmed / Pending / Cancelled)
        #Compare to admin booing lists, style.css
        if status == "Confirmed":
            return "status-confirmed"
        if status == "Pending":
            return "status-pending"
        return "status-cancelled"

    @app.context_processor
    def inject_today():
        #Let the min attribute of the date input tag can block the past date, and using today as default
        return {"today": date.today().isoformat()}


    @app.errorhandler(404)
    def not_found(error): #Error handler, 404 means page not found
        return render_template("error.html", message = 'Page not found.'), 404

    #Compare to server.js initializeRooms() ; If the rooms collection is empty, then insert the default rooms when starting
    try:
        room_manager.set_defaults()
    except Exception as exc: # When disconnect the database, the app can still running and print the error message
        print(f"Failed to initialize room: {exc}")

    return app

app = create_app() #Create the app, flask run, gunicorn app will find this variable

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", 3000)), debug=True)
    #host="127.0.0.1": only allow local connection
    #port set the environment variable PORT, if not set, use default
    #debug=True: system using auto restart, but do not open debug mode in public server