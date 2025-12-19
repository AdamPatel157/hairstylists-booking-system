from flask import Blueprint, render_template, request, flash, redirect
from flask_login import login_required, current_user

from website.database_management import getBookedSlotIdsForWeek, getDbConnection, getUpcomingAppointments, fetchServices, getSelectedServicesFromIds, getAllBarbers, generateWeeklySlots, getAllTimeSlots, ensureCurrentWeekSlots, getBarberById, getWeekCommencingStrings, getTimeSlotsForWeek
from website.user_friendly_names import userFriendlyServiceNames, userFriendlyCategoryNames
from algorithms.appointment_classes import Appointment, TimeSlot
from algorithms.email_communication import sendBookingConfirmationEmail
from algorithms.validation_functions import validateSlots, isSlotInPast
from algorithms.miscellaneous_functions import getActualDate, calculateRequiredSlots, getSlotStartTimeInMinutes

views = Blueprint("views", __name__)

activeAppointments = {}
# Holds Appointment objects with the current_user.customerId key


@views.route("/")
def home():
    return render_template("index.html")


@views.route("/customer_dashboard")
@login_required
def customerDashboard():
    return render_template(
        "webpages/customer_facing/customer_dashboard.html",
        firstName = current_user.firstName,
        isBlacklisted = bool(current_user.isBlacklisted),
        nav_context = "dashboard"
    )


@views.route("/view_appointments")
@login_required
def viewAppointments():

    customerID = current_user.getCustomerId()
    bookings = getUpcomingAppointments(customerID)

    return render_template("webpages/customer_facing/view_appointments.html", appointments = bookings, nav_context = "view_appointments")


@views.route("/select_services", methods = ["GET", "POST"])
@login_required
def selectServices():
    servicesByCategory = fetchServices()

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
                flash("You can only select one service from the Haircut category", "Error")

            elif hairWashAndDryChoices > 1:
                flash("You can only select one service from the Hair Wash and Dry category", "Error")

            elif hairColourChoices > 1:
                flash("You can only select one Hair Dye Colour", "Error")

            elif beardStylingChoices > 1:
                flash("You can only select one service from the Beard Styling category", "Error")

            elif beardWashAndDryChoices > 1:
                flash("You can only select one service from the Beard Wash and Dry category", "Error")

            else:
                selectedServices = getSelectedServicesFromIds(service for service in selectedIds)
                timeDuration = sum(int(service["duration"]) for service in selectedServices)

                if timeDuration < 14:
                    flash("You have not selected enough services for the minimum time requirement of an appointment.",
                          "Error")
                else:
                    valid = True

            if valid:
                flash("Your choices have been successfully selected. Please proceed when ready.", "Success")
                selectedServices = getSelectedServicesFromIds(service for service in selectedIds)
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

            selectedServices = getSelectedServicesFromIds(selectedIds)

            appointment = Appointment(current_user.customerId)
            print(request.form)
            for service in selectedServices:
                appointment.addService(
                    serviceId = service["serviceId"],
                    price = float(service["price"]),
                    duration = int(service["duration"])
                )

            activeAppointments[current_user.customerId] = appointment

            return redirect("/select_barber")

        # If user wishes to re-choose options
        elif action == "reset":
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


@views.route("/select_barber", methods = ["GET", "POST"])
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

    # Ensures current week slots records have been created
    ensureCurrentWeekSlots()

    weekCommencingStr, weekCommencingDisplay = getWeekCommencingStrings()

    days = ["Tue", "Wed", "Thu", "Fri", "Sat"]
    timeIntervals = []
    for hour in range(10, 18):
        for minute in (0, 20, 40):
            formattedTime = f"{hour:02d}:{minute:02d}"
            timeIntervals.append(formattedTime)

    duration = appointment.getTotalDuration()
    requiredSlotCount = calculateRequiredSlots(duration)

    barber = getBarberById(appointment.getBarberId())
    barberName = f"{barber['FirstName']} {barber['LastName']}"

    # Fetches current-week slots and booked slot ids
    allSlots = getTimeSlotsForWeek(weekCommencingStr)
    bookedSlotIds = getBookedSlotIdsForWeek(weekCommencingStr)

    slotObjects = []
    slotMap = {}
    idToSlot = {}

    for row in allSlots:
        if row["BarberID"] == appointment.getBarberId():
            isBooked = row["SlotID"] in bookedSlotIds
            slot = TimeSlot(
                slotId = row["SlotID"],
                barberId = row["BarberID"],
                dayOfWeek = row["Day"],
                startTime = row["StartTime"],
                endTime = row["EndTime"],
                weekCommencing = row["WeekCommencing"],
                isAvailable = bool(row["IsAvailable"]),
                isSelected = False,
                isBooked = isBooked
            )
            slotObjects.append(slot)
            slotMap[(slot.getDayOfWeek(), slot.getStartTime())] = slot
            idToSlot[slot.getSlotId()] = slot

    weekCommencing = weekCommencingDisplay

    # Reflects previously selected slots into the objects
    selectionLocked = appointment.isSelectionLocked()
    if appointment.getSlotIds():
        for sid in appointment.getSlotIds():
            slot = idToSlot.get(sid)
            if slot:
                slot.setSelected(True)

    if request.method == "POST":
        action = request.form.get("action")

        if action == "validate":
            selectedSlotIds = [int(sid) for sid in request.form.getlist("selectedSlots")]

            if len(selectedSlotIds) != requiredSlotCount:
                flash(f"You must select exactly {requiredSlotCount} time slots.", "Error")

            elif any((not idToSlot[sid].isAvailable()) or idToSlot[sid].isBooked() for sid in selectedSlotIds):
                flash("One or more selected slots are unavailable.", "Error")

            elif not validateSlots(selectedSlotIds, idToSlot):
                flash("Selected slots must be consecutive and on the same day.", "Error")

            elif any(isSlotInPast(idToSlot[sid]) for sid in selectedSlotIds):
                flash("You cannot select a time slot that is already in the past.", "Error")

            else:
                appointment.lockSelection()
                for sid in selectedSlotIds:
                    if sid not in appointment.getSlotIds():
                        appointment.addSlot(sid)
                    idToSlot[sid].setSelected(True)

                flash("Please review your selected time slots and proceed when ready.", "Success")
                selectionLocked = True

        elif action == "proceed":
            if not appointment.isSelectionLocked() or not appointment.getSlotIds():
                flash("Please confirm your slots before proceeding.", "Error")
            else:
                return redirect("/note_for_barber")

        elif action == "reset":
            appointment.unlockSelection()
            appointment.clearSlots()
            for slot in slotObjects:
                slot.setSelected(False)
            flash("Selection has been reset.", "Success")
            selectionLocked = False

    return render_template(
        "webpages/customer_facing/select_time_slot.html",
        appointment = appointment,
        barberName = barberName,
        weekCommencing = weekCommencing,
        requiredSlotCount = requiredSlotCount,
        days = days,
        timeIntervals = timeIntervals,
        slotMap = slotMap,
        selectionLocked = selectionLocked,
        nav_context = "select_time_slot"
    )


@views.route("/note_for_barber", methods = ["GET", "POST"])
@login_required
def noteForBarber():
    appointment = activeAppointments.get(current_user.customerId)

    if not appointment:
        flash("Please select services first.", "Error")
        return redirect("/select_services")

    barberNote = appointment.getNoteForBarber()

    if request.method == "POST":
        action = request.form.get("action")
        noteInput = request.form.get("noteForBarber", "").strip()

        if action == "confirm":
            if len(noteInput) > 250:
                flash("Note must not exceed 250 characters.", "Error")
            else:
                appointment.setNoteForBarber(noteInput)
                flash("Note saved successfully.", "Success")
                return redirect("/confirm_booking")

    return render_template(
        "webpages/customer_facing/note_for_barber.html",
        noteForBarber = barberNote,
        nav_context = "note_for_barber"
    )


@views.route("/confirm_booking", methods = ["GET", "POST"])
@login_required
def confirmBooking():
    appointment = activeAppointments.get(current_user.customerId)

    if not appointment or not appointment.isSelectionLocked():
        flash("Please complete your slot selection first.", "Error")
        return redirect("/select_time_slot")

    serviceIds = appointment.getServiceIds()
    slotIds = appointment.getSlotIds()
    barberId = appointment.getBarberId()

    if not serviceIds or not slotIds or not barberId:
        flash("Incomplete appointment details.", "Error")
        return redirect("/select_services")

    selectedServices = getSelectedServicesFromIds(serviceIds)

    barber = getBarberById(barberId)
    barberName = f"{barber['FirstName']} {barber['LastName']}"

    allSlots = getAllTimeSlots()
    slotDetails = [row for row in allSlots if row["SlotID"] in slotIds]

    # Sorts slots by start time
    slotDetails.sort(key = lambda s: s["StartTime"])

    weekCommencing = slotDetails[0]["WeekCommencing"]
    selectedDay = slotDetails[0]["Day"]
    selectedDate = getActualDate(weekCommencing, selectedDay)

    startTime = slotDetails[0]["StartTime"]
    endTime = slotDetails[-1]["EndTime"]

    totalPrice = appointment.getTotalPrice()
    barberNote = appointment.getNoteForBarber()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "confirm":

            appointment.setDate(selectedDate)
            appointment = activeAppointments.get(current_user.customerId)

            conn = getDbConnection()

            if appointment.addBookingToDatabase(conn):
                sendBookingConfirmationEmail(appointment.getBookingReference())
                flash("Booking confirmed successfully.", "Success")
                return redirect(f"/booking_confirmed?ref={appointment.getBookingReference()}")

            else:
                flash("There was a problem confirming your booking.", "Error")
                return redirect("/confirm_booking")

    return render_template(
        "webpages/customer_facing/confirm_booking.html",
        appointment = appointment,
        selectedServices = selectedServices,
        selectedDate = selectedDate,
        startTime = startTime,
        endTime = endTime,
        barberName = barberName,
        totalPrice = totalPrice,
        noteForBarber = barberNote,
        nav_context = "confirm_booking"
    )


@views.route("/booking_confirmed")
@login_required
def bookingConfirmed():
    bookingReference = request.args.get("ref", type = int)

    if not bookingReference:
        return render_template(
            "webpages/customer_facing/booking_confirmed.html",
            bookingReference = "Unavailable",
            nav_context = "booking_confirmed"
        )

    return render_template(
        "webpages/customer_facing/booking_confirmed.html",
        bookingReference = bookingReference,
        nav_context = "booking_confirmed"
    )
