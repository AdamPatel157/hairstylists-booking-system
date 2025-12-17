from flask import Blueprint, render_template, flash, redirect, request
from flask_login import login_required, current_user

from algorithms.email_communication import sendCancellationEmail
from website.database_management import getBarberById, getRevenueDataForWeek, getScheduleForWeek, getCustomerEmailByBookingRef, cancelAppointmentByBookingRef, getWeekCommencingStrings
from .user_friendly_names import userFriendlyServiceNames, userFriendlyCategoryNames

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

    weekCommencingStr, weekCommencingDisplay = getWeekCommencingStrings()

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
        week_commencing = weekCommencingDisplay,
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

    weekCommencingStr, weekCommencingDisplay = getWeekCommencingStrings()

    rows = getScheduleForWeek(barberId, weekCommencingStr)

    schedule = {day: [] for day in ["Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]}

    for row in rows:
        rawServices = row["Services"].split(", ") if row["Services"] else []
        rawCategories = row["Categories"].split(", ") if row["Categories"] else []

        friendlyServices = []
        for serviceName, categoryName in zip(rawServices, rawCategories):
            friendlyService = userFriendlyServiceNames(serviceName)
            friendlyCategory = userFriendlyCategoryNames(categoryName)

            if friendlyCategory == "Hair Wash and Dry":
                if "Rinse" in friendlyService:
                    friendlyService = friendlyService.replace("Rinse", "Hair Rinse")
                elif "Wash" in friendlyService:
                    friendlyService = friendlyService.replace("Wash", "Hair Wash")
                elif "Conditioner" in friendlyService:
                    friendlyService = friendlyService.replace("Conditioner Wash", "Hair Conditioner Wash")

            elif friendlyCategory == "Beard Wash and Dry":
                if "Rinse" in friendlyService:
                    friendlyService = friendlyService.replace("Rinse", "Beard Rinse")
                elif "Wash" in friendlyService:
                    friendlyService = friendlyService.replace("Wash", "Beard Wash")
                elif "Conditioner" in friendlyService:
                    friendlyService = friendlyService.replace("Conditioner Wash", "Beard Conditioner Wash")

            friendlyServices.append(friendlyService)

        appt = {
            "BookingReference": row["BookingReference"],
            "Day": row["Day"],
            "Date": row["Date"],
            "StartTime": row["StartTime"],
            "EndTime": row["EndTime"],
            "CustomerName": f'{row["FirstName"]} {row["LastName"]}',
            "TotalPrice": round((row["TotalPrice"] or 0.0) + 5.00, 2),
            "Services": ", ".join(friendlyServices),
            "Note": row["NoteForBarber"]
        }

        fullDayName = {
            "Tue": "Tuesday",
            "Wed": "Wednesday",
            "Thu": "Thursday",
            "Fri": "Friday",
            "Sat": "Saturday"
        }.get(row["Day"], row["Day"])

        if fullDayName in schedule:
            schedule[fullDayName].append(appt)

    return render_template(
        "webpages/barber_facing/view_schedule.html",
        firstName = firstName,
        is_admin = isAdmin,
        week_commencing = weekCommencingDisplay,
        schedule = schedule
    )

@barberRedirection.route("/cancel_appointment", methods = ["POST"])
@login_required
def cancelAppointment():
    bookingRef = request.form.get("booking_ref")
    cancelReason = request.form.get("cancel_reason")

    if not bookingRef or not cancelReason:
        flash("Missing booking reference or cancellation reason.", category = "Error")
        return redirect("/view_schedule")

    try:
        bookingRefInt = int(bookingRef)
    except ValueError:
        flash("Invalid booking reference format.", category = "Error")
        return redirect("/view_schedule")

    customerEmail = getCustomerEmailByBookingRef(bookingRefInt)
    if customerEmail:
        sendCancellationEmail(customerEmail, bookingRefInt, cancelReason)

    success = cancelAppointmentByBookingRef(bookingRefInt)
    if success:
        flash(f"Appointment {bookingRefInt} successfully cancelled.", category="Success")
    else:
        flash(f"No appointment found with booking reference {bookingRefInt}.", category="Error")

    return redirect("/view_schedule")