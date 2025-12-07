from flask import Blueprint, render_template, request

from flask_login import login_required, current_user

from website.database_management import fetch_services, get_selected_services_from_ids
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
    servicesByCategory = fetch_services()  # your existing function

    if request.method == "POST":
        action = request.form.get("action")   # "recalculate" or "continue"
        selected_ids = request.form.getlist("service")

        # Validate Select-One categories
        single_select = {"Haircuts", "Beard Wash and Dry", "Hair Wash and Dry", "Beard Styling"}
        errors = []

        for category, services in servicesByCategory.items():
            if category in single_select:
                count = sum(1 for s in services if str(s['serviceId']) in selected_ids)
                if count > 1:
                    errors.append(f"You may only choose one option from {category}.")

        # If validation errors, stay on page
        if errors:
            for e in errors:
                flash(e, "Error")
            selectedServices = get_selected_services_from_ids(selected_ids)
            totalPrice = 5 + sum(s["price"] for s in selectedServices)
            totalDuration = sum(s["duration"] for s in selectedServices)
            return render_template(
                "webpages/customer_facing/select_services.html",
                servicesByCategory=servicesByCategory,
                selectedServices=selectedServices,
                selectedServiceIds=selected_ids,
                totalPrice=totalPrice,
                totalDuration=totalDuration,
                summaryReady=True,
                nav_context="select_services"
            )

        # If user clicked "continue" → pass boolean flags to next procedure
        if action == "continue":
            # Build boolean flags
            all_ids = []
            for cat in servicesByCategory.values():
                for s in cat:
                    all_ids.append(str(s['serviceId']))

            boolean_flags = {sid: sid in selected_ids for sid in all_ids}

            # Call your next step
            return proceed_to_barber_selection(boolean_flags)

        # If user clicked "recalculate"
        if action == "recalculate":
            selectedServices = get_selected_services_from_ids(selected_ids)
            totalPrice = 5 + sum(s["price"] for s in selectedServices)
            totalDuration = sum(s["duration"] for s in selectedServices)

            return render_template(
                "webpages/customer_facing/select_services.html",
                servicesByCategory=servicesByCategory,
                selectedServices=selectedServices,
                selectedServiceIds=selected_ids,
                totalPrice=totalPrice,
                totalDuration=totalDuration,
                summaryReady=True,
                nav_context = "select_services"
            )

    # GET request
    return render_template(
        "webpages/customer_facing/select_services.html",
        servicesByCategory=servicesByCategory,
        selectedServices=[],
        selectedServiceIds=[],
        totalPrice=5,
        totalDuration=0,
        summaryReady = False,
        nav_context = "select_services"
    )