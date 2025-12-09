from flask import Blueprint, render_template, request, flash, redirect

from flask_login import login_required, current_user

from website.database_management import fetch_services, get_selected_services_from_ids, getAllBarbers, generateWeeklySlots, getAllTimeSlots, ensureCurrentWeekSlots, get_barber_by_id
from website.user_friendly_names import user_friendly_service_names, user_friendly_category_names
from algorithms.appointment_classes import Appointment, TimeSlot

views = Blueprint("views", __name__)

activeAppointments = {}
# Holds Appointment objects with the current_user.customerId key

def calculateRequiredSlots(duration: int):
    remainder = duration % 20
    return duration // 20 if remainder < 10 else (duration // 20) + 1

def validateSlots(slotIds, idToSlot):
    # Must have at least one slot
    if not slotIds:
        return False

    # Resolve slots
    slots = [idToSlot.get(int(sid)) for sid in slotIds]
    if any(s is None for s in slots):
        return False

    # All on same day
    day = slots[0].getDayOfWeek()
    if any(s.getDayOfWeek() != day for s in slots):
        return False

    # Sorts by start time
    def toMinutes(t: str):
        hh, mm = t.split(":")
        result = (int(hh) * 60) + int(mm)
        return result

    slots.sort(key = lambda s: toMinutes(s.getStartTime()))

    # Check each consecutive pair differs by exactly 20 minutes
    for i in range(1, len(slots)):
        if toMinutes(slots[i].getStartTime()) - toMinutes(slots[i - 1].getStartTime()) != 20:
            return False

    return True

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

            selectedServices = get_selected_services_from_ids(selectedIds)

            appointment = Appointment(current_user.customerId)
            print(request.form)
            for service in selectedServices:
                appointment.addService(
                    serviceId=service["serviceId"],
                    price=float(service["price"]),
                    duration=int(service["duration"])
                )

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

    days = ["Tue", "Wed", "Thu", "Fri", "Sat"]

    timeIntervals = []

    for hour in range(10, 18):
        for minute in (0, 20, 40):
            formattedTime = f"{hour:02d}:{minute:02d}"
            timeIntervals.append(formattedTime)

    duration = appointment.getTotalDuration()
    requiredSlotCount = calculateRequiredSlots(duration)

    barber = get_barber_by_id(appointment.getBarberId())
    barberName = f"{barber["FirstName"]} {barber["LastName"]}"

    # Builds slots for the barber
    allSlots = getAllTimeSlots()
    slotObjects = []
    slotMap = {}
    idToSlot = {}

    for row in allSlots:
        if row["BarberID"] == appointment.getBarberId():
            slot = TimeSlot(
                slotId = row["SlotID"],
                barberId = row["BarberID"],
                dayOfWeek = row["Day"],
                startTime = row["StartTime"],
                endTime = row["EndTime"],
                weekCommencing = row["WeekCommencing"],
                isAvailable = bool(row["IsAvailable"]),
                isSelected = False
            )
            slotObjects.append(slot)
            slotMap[(slot.getDayOfWeek(), slot.getStartTime())] = slot
            idToSlot[slot.getSlotId()] = slot

    weekCommencing = slotObjects[0].getWeekCommencing() if slotObjects else "Unknown"

    # Reflect any previously selected/locked slots into the objects
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

            # Validate number of slots
            if len(selectedSlotIds) != requiredSlotCount:
                flash(f"You must select exactly {requiredSlotCount} time slots.", "Error")

            # Ensures selected slots are available
            elif any(not idToSlot[sid].isAvailable() for sid in selectedSlotIds):
                flash("One or more selected slots are unavailable.", "Error")

            # Validate consecutive and same day
            elif not validateSlots(selectedSlotIds, idToSlot):
                flash("Selected slots must be consecutive and on the same day.", "Error")

            else:
                appointment.lockSelection()

                # Passes selected slots into appointment class
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

            appointment.clearSlots()
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

@views.route("/note_for_barber", methods=["GET", "POST"])
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
                return redirect("/confirm_appointment")

    return render_template(
        "webpages/customer_facing/note_for_barber.html",
        noteForBarber = barberNote,
        nav_context = "note_for_barber"
    )
