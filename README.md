#Hotel Booking System (Python / Jinja / Flask version)
IFN636 Assessment - Hotel Room Booking System, converted from Node.js + Express to Python + Flask.

#Deployment URL
- **Live Demo URL:**http://hotel-ALB-366595900.ap-southeast-2.elb.amazonaws.com
- **EC2 Instance Name/ID:**
- Server 1- HotelSystem / i-071e429fd39f07fb3
- Server 2- HotelServer2 / i-068f135c5a610e489
- **Tagged Release:** v1.0.0 (https://github.com/hsuanyeh108/Hotel-Booking-System-For-Assignment-2/releases/tag/v1.0.0)

#Architecture Summary
Server-rendered web application for guests (search / book / cancel rooms) and hotel admins (manage bookings and room types).
- **Frontend:** Jinja2 templates (`templates/`) + CSS (`static/style.css`) and Image.
- **Backend:** Python 3 + Flask, split into Blueprints: `guest_routes` (guest pages), `admin_routes` (admin pages, session login) and `api_routes` (JSON API, JWT login).
- **Database:** MongoDB Atlas via PyMongo. Collections: `rooms`, `bookings`, `admins`, `counters`,`notifications` .
- **Cloud Infrastructure:** AWS EC2 (Ubuntu) - deployment steps to be added in the CI/CD step.

#Project Structure
```
app.py              Flask app factory + entry point
config.py           MongoDB connection (reads .env)
models/             Database functions (RoomManager.py, BookingManager.py, AdminManager.py, tools.py)
routes/             guest_routes.py / admin_routes.py / api_routes.py
services/           New functionality for Assessment 2 (see below)
templates/          Jinja2 HTML pages
static/             style.css, img/ (room photos)
tests/              pytest Functional Tests (uses mongomock, no real DataBase needed)
github/workflows    ci.yml for CI/CD Tests
```

#New Functionality for Assessment 2
#1. Pricing & Promotion (Josh) — 
`services/BookingFacade.py`, `services/LongStayPricing.py`, `services/PricingRuleFactory.py` , `services/StandardPricing.py`, `services/WeekendPricing.py`
- **New Functional Requirement**: Admin-defined pricing rules (Standard / Weekend Surcharge +20% / Long Stay Discount -10% for 7+ nights) are automatically applied when a booking is created.
- **Design Pattern: Factory Pattern** — `PricingRuleFactory.get_rule(pricing_type)` returns the correct `PricingRule` subclass without the caller needing to know which concrete class exists.
- **OOP Principles: **Polymorphism** (`book_room()` calls `rule.apply()` without knowing the concrete subclass).
- **New Non-Functional Requirement**: Adding a new pricing rule must not require changes to `book_room()` or any API route (Open/Closed Principle) — demonstrated by the `_REGISTRY` dict being the only thing that changes when a rule is added.
- Entry point used elsewhere: `GET /api/pricing/rules`, and `pricing_type` field on `POST /api/bookings`.

#2. Notification Setting (Sarah) — 
`services/NoficationContract.py` , `services/NotificationService.py`, `services/LoginDecorator.py`, `services/TokenDecorator.py`
- **New Functional Requirement**: When a booking's status changes (Confirmed / Cancelled), the system notifies the guest through the channels an admin has enabled, all managed from one central settings page.
- **Design Pattern: Singleton Pattern** — `NotificationContract` guarantees only one settings object exists across the whole app (`admin/notifications` page, `/api/admin/notifications`, and every booking status change all read/write the same instance).
- **OOP Principle: Encapsulation** — `NotificationContract`'s internal `_settings` dict is never exposed directly; it's only accessed via `get_setting()` / `set_setting()` / `dict()` (which returns a copy).
- **New Non-Functional Requirement**: Turning a channel on/off from the settings page must take effect immediately for the very next booking status change, without restarting the app (proven by the Singleton being shared, not re-read from disk).
- Entry points: Admin page at `/admin/notifications`, API at `GET/PUT /api/admin/notifications`.

#Setup
Requires Python 3.10+ and a MongoDB Atlas connection string.
```bash
python -m venv venv
venv\Scripts\activate            # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env           # Windows   (Mac/Linux: cp .env.example .env)
```
Then edit `.env` and fill in `MONGO_URI`, `DB_NAME` and `SECRET_KEY`. Never commit `.env` on the GitHub.

#Run
```bash
python app.py
```
Open http://localhost:3000. On first start the 6 default rooms are inserted if the `rooms` collection is empty.

## Main Pages
| URL | Who | What |
|---|---|---|
| `/` | Guest | Search rooms by dates / name, book |
| `/book/<room_id>` | Guest | Booking form |
| `/my-bookings` | Guest | Find a booking by Booking ID + phone, view, cancel |
| `/admin/login`, `/admin/register` | Admin | Account access |
| `/admin/dashboard` | Admin | Counts + shortcuts |
| `/admin/bookings` | Admin | Confirm / cancel bookings |
| `/admin/rooms` | Admin | Add / edit / delete room types |
| `/api/...` | Any client | JSON API (admin endpoints need `Authorization: Bearer <token>`) |

#Functional Testing (pytest)
```bash
pip install -r requirements.txt
pytest tests/ -v
```
Tests use `mongomock` so they run without a real MongoDB connection — safe to run in CI/CD.
Covers: Factory Pattern pricing calculations, Singleton identity, Adapter channel dispatch,
and the full API flow (create booking → confirm → notification sent) with pass/fail.

#API Testing (Postman)
1. Open Postman → Add Collection → Add new request
2. Select the environment in the top-right dropdown.
3. Setting the method (GET / POST / PUT / DELETE) as different functions need.
4. Each folders includes After response scripts to run the pm test.
5. Some folders includes Body (raw) to runs the fields it need.
6. Some folders includes Headers of key and value.
7. Run folders top-to-bottom: **Authentication → Rooms → Bookings → Pricing → Notification Settings**
   (Login saves the JWT automatically; Create Room / Create Booking save their IDs automatically
   for later requests).
8. Each folder includes at least one deliberate error-case request (missing fields, wrong
   password, duplicate-booking, unknown pricing type, no token) so the collection demonstrates
   both success and error-handling evidence for the rubric.

#Known Limitations
- No real payment gateway
- Confirmation email / SMS text is display-only.
- Admin registration is open to anyone (carried over from the original design).
- No CSRF protection on forms.


