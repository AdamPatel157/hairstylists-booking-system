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

    def toDatabaseDict(self):
        # Prepares a dictionary for adding values to tblAppointment
        return {
            "BookingReference": self.__bookingReference,
            "CustomerID": self.__customerId,
            "BarberID": self.__barberId,
            "NoteForBarber": self.__noteForBarber,
            "Date": self.__date
        }

    def getAppointmentServices(self):
        # Returns a list of tuples for tblAppointmentServices
        return [(self.__bookingReference, sid) for sid in self.__serviceIds]

    def getAppointmentSlots(self):
        # Returns a list of tuples for tblAppointmentSlots
        return [(slotId, self.__bookingReference) for slotId in self.__slotIds]

    def _recalculateTotals(self, price: float, duration: int, baseFee: float):
        if len(self.__serviceIds) == 1:
            self.__totalPrice = baseFee + price
        else:
            self.__totalPrice = self.__totalPrice + price
        self.__totalDuration = self.__totalDuration + duration