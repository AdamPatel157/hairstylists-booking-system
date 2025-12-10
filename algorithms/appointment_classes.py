from website.database_management import updateSlotAvailability

class Appointment:
    def __init__(self, customerId: int):
        self.__bookingReference = None
        self.__customerId = customerId
        self.__barberId = None
        self.__noteForBarber = ""
        self.__date = None
        self.__serviceIds = []
        self.__slotIds = []
        self.__totalPrice = 0.0
        self.__totalDuration = 0
        self.__selectionLocked = False

    # Getters

    def getBookingReference(self):
        return self.__bookingReference

    def getCustomerId(self):
        return self.__customerId

    def getBarberId(self):
        return self.__barberId

    def getNoteForBarber(self):
        return self.__noteForBarber

    def getDate(self):
        return self.__date

    def getServiceIds(self):
        return self.__serviceIds.copy()

    def getSlotIds(self):
        return self.__slotIds.copy()

    def getTotalPrice(self):
        return self.__totalPrice

    def getTotalDuration(self):
        return self.__totalDuration

    def isSelectionLocked(self):
        return self.__selectionLocked

    # Setters

    def setBarberId(self, barberId: int):
        self.__barberId = barberId

    def setNoteForBarber(self, note: str):
        self.__noteForBarber = note

    def setDate(self, date):
        self.__date = date

    def setBookingReference(self, bookingReference: int):
        self.__bookingReference = bookingReference

    # Public Methods

    def addService(self, serviceId: int, price: float, duration: int, baseFee: float = 5.0):
        self.__serviceIds.append(serviceId)
        self._recalculateTotals(price, duration, baseFee)

    def addSlot(self, slotId: int):
        self.__slotIds.append(slotId)

    def clearSlots(self):
        self.__slotIds.clear()

    def lockSelection(self):
        self.__selectionLocked = True

    def unlockSelection(self):
        self.__selectionLocked = False

    def toDatabaseDict(self):
        return {
            "BookingReference": self.__bookingReference,
            "CustomerID": self.__customerId,
            "BarberID": self.__barberId,
            "NoteForBarber": self.__noteForBarber,
            "Date": self.__date
        }

    def getAppointmentServices(self):
        return [(self.__bookingReference, sid) for sid in self.__serviceIds]

    def getAppointmentSlots(self):
        return [(slotId, self.__bookingReference) for slotId in self.__slotIds]

    def _recalculateTotals(self, price: float, duration: int, baseFee: float):
        if len(self.__serviceIds) == 1:
            self.__totalPrice = baseFee + price
        else:
            self.__totalPrice += price
        self.__totalDuration += duration

    def insertAppointmentRecord(self, cursor):
        cursor.execute("""
            INSERT INTO tblAppointment (CustomerID, BarberID, NoteForBarber, Date)
            VALUES (:CustomerID, :BarberID, :NoteForBarber, :Date)
        """, {
            "CustomerID": self.__customerId,
            "BarberID": self.__barberId,
            "NoteForBarber": self.__noteForBarber,
            "Date": self.__date
        })
        self.__bookingReference = cursor.lastrowid
        return self.__bookingReference

    def insertAppointmentSlots(self, cursor):
        slotPairs = self.getAppointmentSlots()
        cursor.executemany("""
            INSERT INTO tblAppointmentSlots (SlotID, BookingReference)
            VALUES (?, ?)
        """, slotPairs)

    def insertAppointmentServices(self, cursor):
        servicePairs = self.getAppointmentServices()
        cursor.executemany("""
            INSERT INTO tblAppointmentServices (BookingReference, ServiceID)
            VALUES (?, ?)
        """, servicePairs)

    def addBookingToDatabase(self, conn):
        try:
            conn.execute("BEGIN")
            cursor = conn.cursor()

            self.insertAppointmentRecord(cursor)
            self.insertAppointmentSlots(cursor)
            self.insertAppointmentServices(cursor)

            updateSlotAvailability(cursor, self)

            conn.commit()
            return True
        except Exception as error:
            conn.rollback()
            print("Booking failed:", error)
            return False






class TimeSlot:
    def __init__(self, slotId: int, barberId: int, dayOfWeek: str, startTime: str, endTime: str,
                 weekCommencing: str, isAvailable: bool, isSelected: bool = False):
        self.__slotId = slotId
        self.__barberId = barberId
        self.__dayOfWeek = dayOfWeek
        self.__startTime = startTime
        self.__endTime = endTime
        self.__weekCommencing = weekCommencing
        self.__isAvailable = isAvailable
        self.__isSelected = isSelected

    # Getters
    def getSlotId(self):
        return self.__slotId

    def getBarberId(self):
        return self.__barberId

    def getDayOfWeek(self):
        return self.__dayOfWeek

    def getStartTime(self):
        return self.__startTime

    def getEndTime(self):
        return self.__endTime

    def getWeekCommencing(self):
        return self.__weekCommencing

    def isAvailable(self):
        return self.__isAvailable

    def isSelected(self):
        return self.__isSelected

    # Setters
    def setSelected(self, selected: bool):
        self.__isSelected = selected

    def setAvailable(self, available: bool):
        self.__isAvailable = available

    # Methods
    def toDict(self):
        return {
            "SlotID": self.__slotId,
            "BarberID": self.__barberId,
            "Day": self.__dayOfWeek,
            "StartTime": self.__startTime,
            "EndTime": self.__endTime,
            "WeekCommencing": self.__weekCommencing,
            "IsAvailable": self.__isAvailable,
            "IsSelected": self.__isSelected
        }