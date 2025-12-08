from flask import Flask
# Imports the Flask micro web framework library to develop the system as a website through Python

import os

# Imports the flask SQL toolkit that provides access for relational databases


from flask_login import LoginManager

dbName = "database.db"

def create_app():
    app = Flask (__name__)
    app.config["SECRET KEY"] = "Adam157"
    app.secret_key = b'Adam157'
    # Initialises the website with a private secret key

    from .database_management import init_db, get_customer_by_id, get_barber_by_id
    init_db()
    # Links the flask application to the relational database

    from .views import views
    from .user_redirection import userRedirection
    from .database_management import insert_barbers

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(userRedirection, url_prefix="/")

    create_database(app)
    insert_barbers()

    loginManager = LoginManager()
    loginManager.login_view = "auth.login"
    loginManager.init_app(app)

    @loginManager.user_loader
    def load_user(userId):
        # Flask-Login calls this to reload user from session
        # userId format: "customer_123" or "barber_456"
        from algorithms.user_classes import Customer, Barber

        if userId.startswith("customer_"):
            customerId = int(userId.split("_")[1])
            customerData = get_customer_by_id(customerId)
            if customerData:
                # Construct Customer object from database row
                return Customer(
                    customerId=customerData['CustomerID'],
                    firstName=customerData['FirstName'],
                    middleName=customerData['MiddleName'],
                    lastName=customerData['LastName'],
                    email=customerData['EmailAddress'],
                    hashedPassword=customerData['HashedPassword'],
                    isBlacklisted=customerData['IsBlackListed'],
                    phoneNumber=customerData['PhoneNumber']
                )
        elif userId.startswith("barber_"):
            barberId = int(userId.split("_")[1])
            barberData = get_barber_by_id(barberId)
            if barberData:
                return Barber(
                    barberId=barberData['BarberID'],
                    firstName=barberData['FirstName'],
                    middleName=barberData['MiddleName'],
                    lastName=barberData['LastName'],
                    email=barberData['EmailAddress'],
                    hashedPassword=barberData['HashedPassword'],
                    isAdmin=barberData['IsAdmin']
                )
        return None

    return app

def create_database(app):
    baseDir = os.path.abspath(os.path.dirname(__file__))
    dbPath = os.path.join(baseDir, dbName)
    if not os.path.exists(dbPath):  # If the database does not exist, creates it
        with app.app_context():
            db.create_all()
        print("Successfully created database")