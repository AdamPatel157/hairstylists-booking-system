from flask import Blueprint, render_template, request, flash, redirect

from flask_login import login_required, current_user

from website.database_management import fetch_services, get_selected_services_from_ids, getAllBarbers, generateWeeklySlots, getAllTimeSlots, ensureCurrentWeekSlots, get_barber_by_id
from website.user_friendly_names import user_friendly_service_names, user_friendly_category_names
from algorithms.appointment_classes import Appointment, TimeSlot

views = Blueprint("views", __name__)

activeAppointments = {}
# Holds Appointment objects with the current_user.customerId key

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
    servicesByCategory = fetch_services()

    if request.method == "POST":
        action = request.form.get("action")

        # If user chooses to calculate summary
        if action == "calculate":
            selectedIds = [int(selectedId) for selectedId in request.form.getlist("service")]
            haircutChoices = 0
            hairWashAndDryChoices = 0
            hairColourChoices = 0
            beardStylingChoices = 0
            beardWashAndDryChoices = 0

            for service in selectedIds:
                if int(service) == 1:
                    haircutChoices = haircutChoices + 1

                if int(service) == 2:
                    haircutChoices = haircutChoices + 1

                if int(service) == 3:
                    haircutChoices = haircutChoices + 1

                if int(service) == 4:
                    hairWashAndDryChoices = hairWashAndDryChoices + 1

                if int(service) == 5:
                    hairWashAndDryChoices = hairWashAndDryChoices + 1

                if int(service) == 6:
                    hairWashAndDryChoices = hairWashAndDryChoices + 1

                if int(service) == 7:
                    hairColourChoices = hairColourChoices + 1

                if int(service) == 8:
                    hairColourChoices = hairColourChoices + 1

                if int(service) == 9:
                    hairColourChoices = hairColourChoices + 1

                if int(service) == 10:
                    hairColourChoices = hairColourChoices + 1

                if int(service) == 11:
                    hairColourChoices = hairColourChoices + 1

                if int(service) == 13:
                    beardStylingChoices = beardStylingChoices + 1

                if int(service) == 14:
                    beardStylingChoices = beardStylingChoices + 1

                if int(service) == 15:
                    beardStylingChoices = beardStylingChoices + 1

                if int(service) == 16:
                    beardStylingChoices = beardStylingChoices + 1

                if int(service) == 17:
                    beardWashAndDryChoices = beardWashAndDryChoices + 1

                if int(service) == 18:
                    beardWashAndDryChoices = beardWashAndDryChoices + 1

                if int(service) == 19:
                    beardWashAndDryChoices = beardWashAndDryChoices + 1

            valid = False
            # Service Selection Validation
            if not selectedIds:
                flash("You must select services before proceeding.", "Error")

            elif haircutChoices > 1:
                flash("You can only select one service from the 'Haircut' category", "Error")

            elif hairWashAndDryChoices > 1:
                flash("You can only select one service from the 'Hair Wash and Dry' category", "Error")

            elif hairColourChoices > 1:
                flash("You can only select one Hair Dye Colour", "Error")

            elif beardStylingChoices > 1:
                flash("You can only select one service from the 'Beard Styling' category", "Error")

            elif beardWashAndDryChoices > 1:
                flash("You can only select one service from the 'Beard Wash and Dry' category", "Error")

            else:
                selectedServices = get_selected_services_from_ids(service for service in selectedIds)
                timeDuration = sum(int(service["duration"]) for service in selectedServices)

                if timeDuration < 14:
                    flash("You have not selected enough services for the minimum time requirement of an appointment.",
                          "Error")
                else:
                    valid = True

            if valid:
                flash("Your choices have been successfully selected. Please proceed when ready.", "Success")
                selectedServices = get_selected_services_from_ids(service for service in selectedIds)
                totalPrice = 5 + sum(float(service["price"]) for service in selectedServices)
                totalDuration = sum(int(service["duration"]) for service in selectedServices)

                return render_template(
                    "webpages/customer_facing/select_services.html",
                    servicesByCategory = servicesByCategory,
                    selectedServices = selectedServices,
                    selectedServiceIds = selectedIds,
                    totalPrice = totalPrice,
                    totalDuration = totalDuration,
                    summaryReady = True,
                    nav_context = "select_services"
                )

            else:
                return render_template(
                    "webpages/customer_facing/select_services.html",
                    servicesByCategory = servicesByCategory,
                    selectedServices = [],
                    selectedServiceIds = selectedIds,
                    totalPrice = 5,
                    totalDuration = 0,
                    summaryReady = False,
                    nav_context = "select_services"
                )

        # If user wishes to proceed to next page
        elif action == "continue":
            selectedIds = [int(selectedId) for selectedId in request.form.getlist("service")]
            selectedServices = get_selected_services_from_ids(service for service in selectedIds)

            # Creates an Appointment object with the customer ID and selected services
            appointment = Appointment(current_user.customerId)
            for service in selectedServices:
                appointment.addService(service["serviceId"], service["price"], service["duration"])

            # Adds to dictionary of appointment objects
            activeAppointments[current_user.customerId] = appointment

            return redirect("/select_barber")

        # If user wishes to re-choose options
        elif action == "reset":
            return render_template(
                "webpages/customer_facing/select_services.html",
                servicesByCategory=servicesByCategory,
                selectedServices=[],
                selectedServiceIds=[],
                totalPrice=5,
                totalDuration=0,
                summaryReady=False,
                nav_context="select_services"
            )

    # GET request
    return render_template(
        "webpages/customer_facing/select_services.html",
        servicesByCategory = servicesByCategory,
        selectedServices = [],
        selectedServiceIds = [],
        totalPrice = 5,
        totalDuration = 0,
        summaryReady = False,
        nav_context = "select_services"
    )


@views.route("/select_barber", methods=["GET", "POST"])
@login_required
def selectBarber():
    appointment = activeAppointments.get(current_user.customerId)

    if not appointment:
        flash("Please select services first.", "Error")
        return redirect("/select_services")

    if request.method == "POST":
        chosenBarberId = int(request.form.get("barber"))
        appointment.setBarberId(chosenBarberId)
        ensureCurrentWeekSlots()

        return redirect("/select_time_slot")

    barbers = getAllBarbers()

    return render_template(
        "webpages/customer_facing/select_barber.html",
        barbers = barbers,
        appointment = appointment,
        nav_context = "select_barber"
    )


@views.route("/select_time_slot", methods=["GET", "POST"])
@login_required
def selectSlot():
    appointment = activeAppointments.get(current_user.customerId)

    if not appointment:
        flash("Please select services first.", "Error")
        return redirect("/select_services")

    ensureCurrentWeekSlots()

    # Constants
    days = ["Tue", "Wed", "Thu", "Fri", "Sat"]
    timeIntervals = [f"{hour:02d}:{minute:02d}" for hour in range(10, 18) for minute in (0, 20, 40)]
    requiredSlotCount = appointment.getTotalDuration() // 20

    # Get barber name
    barber = get_barber_by_id(appointment.getBarberId())
    barberName = f"{barber['FirstName']} {barber['LastName']}"

    # Get all slots for this barber and week
    allSlots = getAllTimeSlots()
    slotObjects = []
    slotMap = {}

    for row in allSlots:
        if row["BarberID"] == appointment.getBarberId():
            slot = TimeSlot(
                slotId=row["SlotID"],
                barberId=row["BarberID"],
                dayOfWeek=row["Day"],
                startTime=row["StartTime"],
                endTime=row["EndTime"],
                weekCommencing=row["WeekCommencing"],
                isAvailable=bool(row["IsAvailable"])
            )
            slotObjects.append(slot)
            slotMap[(slot.getDayOfWeek(), slot.getStartTime())] = slot

    # Get week commencing from any slot (they all share it)
    weekCommencing = slotObjects[0].getWeekCommencing() if slotObjects else "Unknown"

    # Handle POST
    if request.method == "POST":
        selectedSlotIds = request.form.getlist("selectedSlots")
        if len(selectedSlotIds) != requiredSlotCount:
            flash(f"You must select exactly {requiredSlotCount} time slots.", "Error")
        else:
            for slotId in selectedSlotIds:
                appointment.addSlot(int(slotId))
            return redirect("/confirm_appointment")

    return render_template(
        "webpages/customer_facing/select_time_slot.html",
        appointment=appointment,
        barberName=barberName,
        weekCommencing=weekCommencing,
        requiredSlotCount=requiredSlotCount,
        days=days,
        timeIntervals=timeIntervals,
        slotMap=slotMap,
        nav_context="select_time_slot"
    )