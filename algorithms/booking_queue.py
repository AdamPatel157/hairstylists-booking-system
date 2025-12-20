import time
from website.database_management import isSlotBooked, getAllTimeSlots, getDbConnection, setSlotAvailability

class BookingQueue:
    def __init__(self, maxSize = 50):
        self.__maxSize = maxSize
        self.__queue = [None] * maxSize
        self.__startPointer = 0
        self.__endPointer = 0
        self.__count = 0


    def isEmpty(self):
        if self.__count == 0:
            return True
        else:
            return False


    def isFull(self):
        if self.__count == self.__maxSize:
            return True
        else:
            return False


    def enqueue(self, request):
        # Until queue is no longer full, waits and retries
        while self.isFull():
            time.sleep(0.2)

        self.__queue[self.__endPointer] = request
        self.__endPointer = (self.__endPointer + 1) % self.__maxSize
        self.__count += 1


    def dequeue(self):
        if self.isEmpty():
            return None

        request = self.__queue[self.__startPointer]
        self.__queue[self.__startPointer] = None
        self.__startPointer = (self.__startPointer + 1) % self.__maxSize
        self.__count -= 1
        return request


    def processNext(self):
        request = self.dequeue()
        if request is None:
            return False

        requestType = request["type"]
        payload = request["payload"]

        if requestType == "Booking":
            return self._processBooking(payload)

        elif requestType == "BlockSlots":
            return self._processBlockSlots(payload)

        else:
            print("Unknown request type:", requestType)
            return False


    def _processBooking(self, payload):
        appointment = payload["appointment"]
        slotIds = appointment.getSlotIds()

        if not self._slotsStillAvailable(slotIds):
            print("Booking failed: slots no longer available.")
            return False

        conn = getDbConnection()
        return appointment.addBookingToDatabase(conn)


    def _processBlockSlots(self, payload):
        slotIds = payload["slotIds"]
        action = payload["action"]

        if action == "block":
            if not self._slotsStillAvailable(slotIds):
                print("Block failed: slot already booked.")
                return False
            for sid in slotIds:
                setSlotAvailability(sid, False)
            return True

        if action == "unblock":
            if not self._slotsNotBooked(slotIds):
                print("Unblock failed: slot is booked.")
                return False
            for sid in slotIds:
                setSlotAvailability(sid, True)
            return True

        return False


    @staticmethod
    def _slotsStillAvailable(slotIds):
        allSlots = getAllTimeSlots()
        slotMap = {row["SlotID"]: row for row in allSlots}

        for sid in slotIds:
            if sid not in slotMap:
                return False
            if slotMap[sid]["IsAvailable"] == 0:
                return False

        return True

    @staticmethod
    def _slotsNotBooked(slotIds):
        for sid in slotIds:
            if isSlotBooked(sid):
                return False
        return True