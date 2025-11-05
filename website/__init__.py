from flask import Flask
# Imports the Flask micro web framework library to develop system as a website through Python

from flask_sqlalchemy import SQLAlchemy
# Imports the flask SQL toolkit that provides access for relational databases

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask (__name__)
    app.config["SECRET KEY"] = "Adam157"
    app.secret_key = b'Adam157'
    # Initialises the website with a private secret key

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)
    # Links the flask application to the relational database

    from .views import views
    from .user_redirection import user_redirection

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(user_redirection, url_prefix="/")

    return app