#pytest Shared Settings：use mongomock replace real MongoDB to connect
#Functional Testing doesn't need to connect to MongoDB Atlas, CI/CD will run faster and more stable
#need to import any models/routes modules before, need to replace config.db with mongomock
#because models/*.py will import db["xxx"] when it is imported

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

import mongomock  # no quality assurance: module level import not at top of file
import backend.config as config # no quality assurance: module level import not at top of file

config.client = mongomock.MongoClient()
config.db = config.client["test_db"]

import pytest  # no quality assurance: module level import not at top of file


@pytest.fixture(autouse=True)
def clean_database():
    #Before every testing, will clear all collections, to ensure each test will not influence each other
    from backend.services.NoficationContract import NotificationContract
    NotificationContract.reset_testing()
    for name in config.db.list_collection_names():
        config.db[name].delete_many({})
    yield


@pytest.fixture
def app():
    from app import create_app
    flask_app = create_app()
    flask_app.config.update(TESTING=True)
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    resp = client.post("/api/auth/register", json={
        "name": "Admin", "email": "admin@test.com", "password": "pass1234"})
    token = resp.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}