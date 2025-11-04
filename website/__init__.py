from flask import Flask
# Imports the Flask micro web framework library to develop system as a website through Python

def create_app():
    app = Flask (__name__)
    app.config["SECRET KEY"] = "Adam157"
    app.secret_key = b'Adam157'
# Configures the website with a private key for admin access

    from .views import views
    from .user_redirection import user_redirection

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(user_redirection, url_prefix="/")

    return app