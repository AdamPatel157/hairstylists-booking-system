from flask import Blueprint, render_template, session, redirect, request

from flask_login import login_required, current_user

from website.database_management import fetch_services, get_selected_services
from website.user_friendly_names import user_friendly_service_names, user_friendly_category_names

# Allows the system to access user-related database manipulation functions

views = Blueprint("views", __name__)

@views.route("/")
def home():
    return render_template("index.html")


@views.route("/customer_dashboard")
@login_required
def customer_dashboard():
    return render_template(
        "webpages/customer_facing/customer_dashboard.html",
        firstName=current_user.firstName,
        nav_context="dashboard"
    )


@views.route("/view_appointments")
@login_required
def view_appointments():
    return render_template(
        "webpages/customer_facing/view_appointments.html",
        nav_context="dashboard")


@views.route("/select_services", methods=["GET", "POST"])
@login_required
def selectServices():
    if request.method == "POST":
        # Retrieves selected service IDs from the form and stores them in the session cookies
        selectedServiceIds = request.form.getlist("service")
        session["selectedServiceIds"] = [str(sid) for sid in selectedServiceIds]
        return redirect("/select_barber")

    # When receving a GET request, pulls service IDs from the session cookies
    selectedServiceIds = session.get("selectedServiceIds", [])

    servicesByCategory = fetch_services()
    selectedServices = get_selected_services()
    return render_template(
        "webpages/customer_facing/select_services.html",
        servicesByCategory=servicesByCategory,
        selectedServices=selectedServices,
        selectedServiceIds=selectedServiceIds,
        nav_context="select_services"
    )