from flask import Blueprint, render_template, flash, redirect
from flask_login import login_required, current_user

from website.database_management import getBarberById

barberRedirection = Blueprint("barberRedirection", __name__)

@barberRedirection.route("/barber_dashboard")
@login_required
def barberDashboard():
    barberId = current_user.barberId
    barberRecord = getBarberById(barberId)

    if not barberRecord:
        flash("Barber record not found.", category = "Error")
        return redirect("/login")

    firstName = barberRecord["FirstName"]
    isAdmin = barberRecord["IsAdmin"] == 1

    return render_template(
        "webpages/barber_facing/barber_dashboard.html",
        firstName = firstName,
        is_admin = isAdmin
    )

@barberRedirection.route("/admin_dashboard")
@login_required
def adminDashboard():
    barberId = current_user.barberId
    barberRecord = getBarberById(barberId)

    if not barberRecord:
        flash("Barber record not found.", category = "Error")
        return redirect("/login")

    if barberRecord["IsAdmin"] != 1:
        flash("Access denied. Admin privileges required.", category = "Error")
        return redirect("/barber_dashboard")

    firstName = barberRecord["FirstName"]

    return render_template(
        "webpages/admin_facing/admin_dashboard.html",
        firstName = firstName,
        is_admin = True
    )