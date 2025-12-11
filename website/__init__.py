from flask import Flask
# Imports the Flask micro web framework library to develop the system as a website through Python

import os

from flask_login import LoginManager

dbName = "database.db"

def createApp():
    app = Flask (__name__)
    app.config["SECRET KEY"] = "Adam157"
    app.secret_key = b'Adam157'
    # Initialises the website with a private secret key

    from .database_management import initDb, getCustomerById, getBarberById

    initDb()
    # Links the flask application to the relational database

    from .views import views
    from .user_redirection import userRedirection
    from .database_management import insertBarbers

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(userRedirection, url_prefix="/")

    createDatabase(app)
    insertBarbers()

    loginManager = LoginManager()
    loginManager.login_view = "auth.login"
    loginManager.init_app(app)

    @loginManager.user_loader
    def loadUser(userId):
        from algorithms.user_classes import Customer, Barber

        if userId.startswith("customer_"):
            customerId = int(userId.split("_")[1])
            customerData = getCustomerById(customerId)
            if customerData:
                # Constructs Customer object from database row
                return Customer(
                    customerId = customerData['CustomerID'],
                    firstName = customerData['FirstName'],
                    middleName = customerData['MiddleName'],
                    lastName = customerData['LastName'],
                    email = customerData['EmailAddress'],
                    hashedPassword = customerData['HashedPassword'],
                    isBlacklisted = customerData['IsBlackListed'],
                    phoneNumber = customerData['PhoneNumber']
                )
        elif userId.startswith("barber_"):
            barberId = int(userId.split("_")[1])
            barberData = getBarberById(barberId)
            if barberData:
                return Barber(
                    barberId = barberData['BarberID'],
                    firstName = barberData['FirstName'],
                    middleName = barberData['MiddleName'],
                    lastName = barberData['LastName'],
                    email = barberData['EmailAddress'],
                    hashedPassword = barberData['HashedPassword'],
                    isAdmin = barberData['IsAdmin']
                )
        return None

    return app

def createDatabase(app):
    baseDir = os.path.abspath(os.path.dirname(__file__))
    dbPath = os.path.join(baseDir, dbName)
    if not os.path.exists(dbPath):  # If the database does not exist, creates it
        with app.app_context():
            db.create_all()
        print("Successfully created database")