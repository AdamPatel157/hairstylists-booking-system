from flask import Blueprint, render_template
from flask_login import login_required, current_user

views = Blueprint("views", __name__)

@views.route("/")
def home():
    return render_template("index.html")

@views.route("/customer_dashboard")
@login_required
def customer_dashboard():
    return render_template("webpages/customer_facing/customer_dashboard.html", firstName=current_user.firstName)
