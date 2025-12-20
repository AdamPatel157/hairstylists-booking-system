from algorithms.time_slot_merge_sort import toMinutes, timeSlotMergeSort
from algorithms.appointment_classes import TimeSlot
from datetime import datetime, timedelta
from flask import flash

import re
# For Regular Expressions

def validateSlots(slotIds, idToSlot):
    if not slotIds:
        return False

    slots = []
    for slotId in slotIds:
        slotObject = idToSlot.get(int(slotId))
        slots.append(slotObject)

    for slot in slots:
        if slot is None:
            return False

    firstSlotDay = slots[0].getDayOfWeek()
    for slot in slots:
        if slot.getDayOfWeek() != firstSlotDay:
            return False

    slots = timeSlotMergeSort(slots)

    # Checks that each consecutive slot starts exactly 20 minutes after the previous one
    for index in range(1, len(slots)):
        currentSlotStart = toMinutes(slots[index].getStartTime())
        previousSlotStart = toMinutes(slots[index - 1].getStartTime())
        difference = currentSlotStart - previousSlotStart

        if difference != 20:
            return False

    # If all checks pass, the slots are valid
    return True


def isSlotInPast(slot: TimeSlot):
    weekCommencing = datetime.strptime(slot.getWeekCommencing(), "%Y-%m-%d")

    dayMap = {"Sun": 0, "Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5, "Sat": 6}
    dayOffset = dayMap[slot.getDayOfWeek()]

    slotDate = weekCommencing + timedelta(days = dayOffset)

    slotDateTime = datetime.strptime(
        f"{slotDate.strftime('%Y-%m-%d')} {slot.getStartTime()}",
        "%Y-%m-%d %H:%M"
    )

    return slotDateTime < datetime.now()


def validateName(name, namePos):
    lowercaseEnglishAlphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    if (len(name) < 2) and (namePos != "Middle"): # Allows empty middle name fields
        flash(f"{namePos} Name must be greater than 1 character long.", category = "Error")
        return False
    elif len(name) > 50:
        flash(f"{namePos} Name cannot be longer than 50 characters.", category="Error")
        return False
    elif any(character.lower() not in lowercaseEnglishAlphabet for character in name):
        flash(f"{namePos} Name can only contain English alphabet characters.", category = "Error")
        return False
    else:
        return True


def validateEmail(emailAddress):
    # Uses Regular Expressions to ensure that emails are of the format: 'user@example.com'
    emailPattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if len(emailAddress) > 254:
        flash("Email address cannot be longer than 254 characters.", category="Error")
        return False

    elif not re.match(emailPattern, emailAddress):
        flash("Please enter a valid email address (e.g., user@example.com).", category = "Error")
        return False

    else:
        return True


def validatePassword(createPassword, confirmPassword):
    passwordPunctuation = ['?', '!', '£', '%', '^', '&', '*', '(', ')', '/', '#']
    lowercaseEnglishAlphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    if len(createPassword) < 8:
        flash("Passwords must be at least 8 characters in length.", category = "Error")
        return False

    elif len(createPassword) > 55:
        # Ensures passwords are suitable for the password hashing algorithm to function correctly
        flash("Passwords cannot be longer than 55 characters.", category = "Error")
        return False

    elif not any(character.lower() in lowercaseEnglishAlphabet for character in createPassword):
        flash("Passwords must contain at least one English alphabet character.", category = "Error")
        return False

    elif not any(character in numbers for character in createPassword):
        flash("Passwords must contain at least one integer number 0-9.", category = "Error")
        return False

    elif not any(character in passwordPunctuation for character in createPassword):
        flash("Passwords must contain at least one punctuation character from ['?', '!', '£', '%', '^', '&', '*', '(', ')', '/', '#'].", category="Error")
        return False

    elif createPassword == createPassword.lower():  # If there are no uppercase letters
        flash("Passwords must contain at least one uppercase letter.", category = "Error")
        return False

    elif createPassword == createPassword.upper():  # If there are no lowercase letters
        flash("Passwords must contain at least one lowercase letter.", category = "Error")
        return False

    elif createPassword != confirmPassword:  # If the confirmation password does not equal the created password
        flash("Passwords do not match.", category = "Error")
        return False

    else:
        return True