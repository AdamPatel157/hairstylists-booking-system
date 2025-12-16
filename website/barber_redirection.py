from flask import Blueprint, render_template, flash, redirect
from flask_login import login_required, current_user
from datetime import date, timedelta

from website.database_management import getBarberById, getRevenueDataForWeek, getScheduleForWeek
from .user_friendly_names import userFriendlyServiceNames

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


@barberRedirection.route("/basic_revenue_view")
@login_required
def basicRevenueView():
    barberId = current_user.getBarberId()
    barberRecord = getBarberById(barberId)

    if not barberRecord:
        flash("Barber record not found.", category="Error")
        return redirect("/login")

    firstName = barberRecord["FirstName"]
    isAdmin = barberRecord["IsAdmin"] == 1

    today = date.today()
    weekCommencing = today - timedelta(days=(today.weekday() + 1) % 7)
    weekCommencingStr = weekCommencing.strftime("%Y-%m-%d")

    revenueRows = getRevenueDataForWeek(barberId, weekCommencingStr)

    days = ["Tue", "Wed", "Thu", "Fri", "Sat"]

    revenueData = {
        day: {
            "appointments": set(),
            "revenue": 0.0
        } for day in days
    }

    for row in revenueRows:
        day = row["Day"]
        bookingRef = row["BookingReference"]
        totalPrice = row["TotalPrice"]

        if day in revenueData:
            if bookingRef not in revenueData[day]["appointments"]:
                revenueData[day]["appointments"].add(bookingRef)
                revenueData[day]["revenue"] += totalPrice

    for day in days:
        appointmentCount = len(revenueData[day]["appointments"])
        revenueData[day]["appointmentCount"] = appointmentCount
        revenueData[day]["revenue"] += appointmentCount * 5.00  # Booking fee
        revenueData[day]["revenue"] = round(revenueData[day]["revenue"], 2)

    totalWeekRevenue = round(
        sum(revenueData[day]["revenue"] for day in days), 2
    )

    return render_template(
        "webpages/barber_facing/basic_revenue_view.html",
        firstName = firstName,
        is_admin = isAdmin,
        week_commencing = weekCommencingStr,
        revenue_data = revenueData,
        total_week_revenue = totalWeekRevenue
    )


@barberRedirection.route("/view_schedule")
@login_required
def viewSchedule():
    barberId = current_user.getBarberId()
    barberRecord = getBarberById(barberId)

    if not barberRecord:
        flash("Barber record not found.", category="Error")
        return redirect("/login")

    firstName = barberRecord["FirstName"]
    isAdmin = barberRecord["IsAdmin"] == 1

    today = date.today()
    weekCommencing = today - timedelta(days=(today.weekday() + 1) % 7)
    weekCommencingStr = weekCommencing.strftime("%Y-%m-%d")

    rows = getScheduleForWeek(barberId, weekCommencingStr)

    schedule = {day: [] for day in ["Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]}

    for row in rows:
        raw_services = row["Services"].split(", ") if row["Services"] else []
        friendly_services = [userFriendlyServiceNames(s) for s in raw_services]

        appt = {
            "BookingReference": row["BookingReference"],
            "Day": row["Day"],
            "Date": row["Date"],
            "StartTime": row["StartTime"],
            "EndTime": row["EndTime"],
            "CustomerName": f'{row["FirstName"]} {row["LastName"]}',
            "TotalPrice": round((row["TotalPrice"] or 0.0) + 5.00, 2),
            "Services": ", ".join(friendly_services),
            "Note": row["NoteForBarber"]
        }

        full_day_name = {
            "Tue": "Tuesday",
            "Wed": "Wednesday",
            "Thu": "Thursday",
            "Fri": "Friday",
            "Sat": "Saturday"
        }.get(row["Day"], row["Day"])

        if full_day_name in schedule:
            schedule[full_day_name].append(appt)

    return render_template(
        "webpages/barber_facing/view_schedule.html",
        firstName = firstName,
        is_admin = isAdmin,
        week_commencing = weekCommencingStr,
        schedule = schedule
    )



