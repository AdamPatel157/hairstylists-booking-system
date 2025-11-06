from flask import Flask
# Imports the Flask micro web framework library to develop the system as a website through Python

import os

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.track_modifications import models_committed

# Imports the flask SQL toolkit that provides access for relational databases

db = SQLAlchemy()
dbName = "database.db"

def create_app():
    app = Flask (__name__)
    app.config["SECRET KEY"] = "Adam157"
    app.secret_key = b'Adam157'
    # Initialises the website with a private secret key

    baseDir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(baseDir, dbName)}"
    db.init_app(app)
    # Links the flask application to the relational database

    from .views import views
    from .user_redirection import user_redirection

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(user_redirection, url_prefix="/")

    # noinspection PyUnresolvedReferences
    from .models import tblCustomer, tblBarber, tblAppointment, tblService, tblTimeSlot, tblAppointmentSlots, tblAppointmentServices

    create_database(app)

    return app

def create_database(app):
    baseDir = os.path.abspath(os.path.dirname(__file__))
    dbPath = os.path.join(baseDir, dbName)
    if not os.path.exists(dbPath):  # If the database does not exist, creates it
        with app.app_context():
            db.create_all()
        print("Successfully created database")