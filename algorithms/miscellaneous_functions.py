from datetime import datetime, timedelta

def getActualDate(weekCommencing: str, dayAbbrev: str):
    baseDate = datetime.strptime(weekCommencing, "%Y-%m-%d")
    offsets = {
        "Sun": 0, "Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5, "Sat": 6
    }
    offsetDays = offsets.get(dayAbbrev, 0)
    actualDate = baseDate + timedelta(days = offsetDays)
    return actualDate.strftime("%d-%m-%Y")


def calculateRequiredSlots(duration: int):
    remainder = duration % 20
    return duration // 20 if remainder < 10 else (duration // 20) + 1


def getSlotStartTimeInMinutes(slot):
    startTime = slot.getStartTime()
    startTimeInMinutes = toMinutes(startTime)
    return startTimeInMinutes