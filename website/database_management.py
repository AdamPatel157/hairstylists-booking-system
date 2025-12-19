import sqlite3
import os

from website.user_friendly_names import userFriendlyServiceNames, userFriendlyCategoryNames

from datetime import datetime, timedelta, date

databasePath = os.path.join(os.path.dirname(__file__), "database.db")

def getDbConnection():
    conn = sqlite3.connect(databasePath)
    conn.row_factory = sqlite3.Row
    # row_factory returns SQL Statement results in dictionaries
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initDb():
    conn = getDbConnection()
    cursor = conn.cursor()

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS tblCustomer
                   (
                       CustomerID
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       FirstName
                       TEXT
                       NOT
                       NULL,
                       MiddleName
                       TEXT,
                       LastName
                       TEXT
                       NOT
                       NULL,
                       EmailAddress
                       TEXT
                       UNIQUE
                       NOT
                       NULL,
                       HashedPassword
                       TEXT
                       NOT
                       NULL,
                       IsBlackListed
                       INTEGER
                       DEFAULT
                       0,
                       PhoneNumber
                       TEXT
                   )
                   """)

    # Barber table - stores barber/admin accounts
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS tblBarber
                   (
                       BarberID
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       FirstName
                       TEXT
                       NOT
                       NULL,
                       MiddleName
                       TEXT,
                       LastName
                       TEXT
                       NOT
                       NULL,
                       EmailAddress
                       TEXT
                       UNIQUE
                       NOT
                       NULL,
                       HashedPassword
                       TEXT
                       NOT
                       NULL,
                       IsAdmin
                       INTEGER
                       DEFAULT
                       0,
                       YearsOfExperience
                       INTEGER
                   )
                   """)

    # Temporary storage for email verification and password resets
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS tblUnverified
                   (
                       UnverifiedID
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       FirstName
                       TEXT
                       NOT
                       NULL,
                       MiddleName
                       TEXT,
                       LastName
                       TEXT
                       NOT
                       NULL,
                       EmailAddress
                       TEXT
                       NOT
                       NULL,
                       HashedPassword
                       TEXT
                       NOT
                       NULL,
                       PhoneNumber
                       TEXT,
                       VerificationCode
                       TEXT
                       NOT
                       NULL,
                       IsPasswordReset
                       INTEGER
                       DEFAULT
                       0,
                       CodeCreatedAt
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   """)

    # Service table - stores available haircut services with pricing
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS tblService
                   (
                        ServiceID
                        INTEGER 
                        PRIMARY KEY 
                        AUTOINCREMENT,
                        ServiceName
                        TEXT    
                        NOT NULL,
                        Duration
                        INTEGER 
                        NOT NULL,
                        Price
                        REAL
                        NOT NULL,
                        ServiceCategory
                        TEXT
                        NOT NULL
                   )
                   """)

    # TimeSlot table - stores barber availability slots
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS tblTimeSlot
                   (
                        SlotID         
                        INTEGER 
                        PRIMARY KEY 
                        AUTOINCREMENT,
                        Day            
                        TEXT    
                        NOT NULL,
                        StartTime
                        TEXT
                        NOT NULL,
                        EndTime   
                        TEXT 
                        NOT NULL,
                        WeekCommencing
                        TEXT
                        NOT NULL,
                        IsAvailable
                        INTEGER
                        DEFAULT
                        1,
                        BarberID
                        INTEGER
                        NOT NULL,
                        FOREIGN KEY (BarberID) 
                        REFERENCES tblBarber (BarberID)
                   )
                   """)

    # Appointment table - stores customer bookings
    # Links customers to barbers with booking date and notes
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS tblAppointment
                   (
                        BookingReference 
                        INTEGER 
                        PRIMARY KEY 
                        AUTOINCREMENT,
                        Date             
                        TIMESTAMP 
                        DEFAULT 
                        CURRENT_TIMESTAMP,
                        NoteForBarber    
                        TEXT,
                        BarberID         
                        INTEGER 
                        NOT NULL,
                        CustomerID       
                        INTEGER 
                        NOT NULL,
                        FOREIGN KEY (BarberID) 
                        REFERENCES tblBarber (BarberID),
                        FOREIGN KEY (CustomerID) 
                        REFERENCES tblCustomer (CustomerID)
                   )
                   """)

    # AppointmentSlots table - link table linking appointments to time slots
    # Composite primary key (SlotID, BookingReference)
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS tblAppointmentSlots
                   (
                        SlotID    
                        INTEGER 
                        NOT NULL,
                        BookingReference 
                        INTEGER 
                        NOT NULL,
                        PRIMARY KEY (SlotID, BookingReference),
                        FOREIGN KEY (SlotID) 
                        REFERENCES tblTimeSlot (SlotID),
                        FOREIGN KEY (BookingReference) 
                        REFERENCES tblAppointment (BookingReference)
                   )
                   """)

    # AppointmentServices table - junction table linking appointments to services
    # Allows multiple services per appointment (many-to-many relationship)
    # Composite primary key (ServiceID, BookingReference)
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS tblAppointmentServices
                   (
                        ServiceID        
                        INTEGER 
                        NOT NULL,
                        BookingReference
                        INTEGER 
                        NOT NULL,
                        PRIMARY KEY (ServiceID, BookingReference),
                        FOREIGN KEY (ServiceID) 
                        REFERENCES tblService (ServiceID),
                        FOREIGN KEY (BookingReference) 
                        REFERENCES tblAppointment (BookingReference)
                   )
                   """)

    # Adds services details to tblService if table is empty

    cursor.execute("SELECT COUNT(*) FROM tblService")
    count = cursor.fetchone()[0]

    if count == 0:
        defaultServices = [
            ("MachineOnly", 14, 7.00, "Haircuts"),
            ("MachineAndScissor", 20, 10.00, "Haircuts"),
            ("SkinFade", 30, 15.00, "Haircuts"),
            ("WaterOnlyRinse", 4, 2.00, "HairWashAndDry"),
            ("ShampooWash", 8, 4.00, "HairWashAndDry"),
            ("ShampooAndConditionerWash", 12, 6.00, "HairWashAndDry"),
            ("BlackDye", 40, 40.00, "HairColour"),
            ("DarkBrownDye", 40, 40.00, "HairColour"),
            ("MediumBrownDye", 40, 40.00, "HairColour"),
            ("LightBrownDye", 40, 40.00, "HairColour"),
            ("BlondeDye", 40, 40.00, "HairColour"),
            ("Bleach", 60, 30.00, "HairColour"),
            ("BeardTrim", 10, 5.00, "BeardStyling"),
            ("BeardLineup", 10, 5.00, "BeardStyling"),
            ("BeardTrimAndLineup", 20, 10.00, "BeardStyling"),
            ("BeardCleanShave", 20, 10.00, "BeardStyling"),
            ("WaterOnlyRinse", 2, 1.00, "BeardWashAndDry"),
            ("ShampooWash", 6, 3.00, "BeardWashAndDry"),
            ("ShampooAndConditionerWash", 10, 5.00, "BeardWashAndDry"),
            ("BeardOil", 2, 1.00, "BeardMiscellaneous"),
            ("BeardFragrance", 2, 1.00, "BeardMiscellaneous"),
            ("HotTowel", 2, 1.00, "BeardMiscellaneous"),
        ]

        cursor.executemany("""
                           INSERT INTO tblService (ServiceName, Duration, Price, ServiceCategory)
                           VALUES (?, ?, ?, ?)
                           """, defaultServices)

    conn.commit()
    conn.close()

# Cross-Parameterised SQL Statements

def getBookingDetails(bookingReference: int):
    # Gets appointment details from the booking reference number and returns as a dictionary
    conn = getDbConnection()
    cursor = conn.cursor()

    try:
        appointmentRow = cursor.execute("""
            SELECT 
                tblAppointment.BookingReference,
                tblAppointment.Date,
                tblAppointment.NoteForBarber,
                tblCustomer.FirstName AS CustomerFirstName,
                tblCustomer.LastName AS CustomerLastName,
                tblCustomer.EmailAddress AS CustomerEmail,
                tblBarber.FirstName AS BarberFirstName,
                tblBarber.LastName AS BarberLastName
            FROM tblAppointment
            JOIN tblCustomer ON tblAppointment.CustomerID = tblCustomer.CustomerID
            JOIN tblBarber ON tblAppointment.BarberID = tblBarber.BarberID
            WHERE tblAppointment.BookingReference = ?
        """, (bookingReference,)).fetchone()

        if not appointmentRow:
            return None

        slotRows = cursor.execute("""
            SELECT 
                tblTimeSlot.Day,
                tblTimeSlot.StartTime,
                tblTimeSlot.EndTime,
                tblTimeSlot.WeekCommencing
            FROM tblAppointmentSlots
            JOIN tblTimeSlot ON tblAppointmentSlots.SlotID = tblTimeSlot.SlotID
            WHERE tblAppointmentSlots.BookingReference = ?
            ORDER BY tblTimeSlot.StartTime
        """, (bookingReference,)).fetchall()

        serviceRows = cursor.execute("""
            SELECT 
                tblService.ServiceName,
                tblService.Duration,
                tblService.Price
            FROM tblAppointmentServices
            JOIN tblService ON tblAppointmentServices.ServiceID = tblService.ServiceID
            WHERE tblAppointmentServices.BookingReference = ?
        """, (bookingReference,)).fetchall()

        totalDuration = sum(row["Duration"] for row in serviceRows)
        totalPrice = sum(row["Price"] for row in serviceRows)

        serviceNames = [row["ServiceName"] for row in serviceRows]

        startTime = slotRows[0]["StartTime"]
        endTime = slotRows[-1]["EndTime"]
        selectedDate = appointmentRow["Date"]
        selectedDay = slotRows[0]["Day"]

        customerName = appointmentRow["CustomerFirstName"] + " " + appointmentRow["CustomerLastName"]
        barberName = appointmentRow["BarberFirstName"] + " " + appointmentRow["BarberLastName"]

        return {
            "bookingReference": bookingReference,
            "customerName": customerName,
            "customerEmail": appointmentRow["CustomerEmail"],
            "selectedDate": selectedDate,
            "selectedDay": selectedDay,
            "startTime": startTime,
            "endTime": endTime,
            "haircutDuration": totalDuration,
            "totalPrice": totalPrice,
            "barberName": barberName,
            "services": serviceNames,
            "noteForBarber": appointmentRow["NoteForBarber"]
        }

    except sqlite3.Error as error:
        print("Database error occurred:", error)
        return None

    except:
        print("An unexpected error occurred.")
        return None

    finally:
        conn.close()


def getUpcomingAppointments(customerID: int):
    conn = getDbConnection()
    cursor = conn.cursor()

    try:
        # Gets appointments with barber and slot info
        appointmentRows = cursor.execute("""
            SELECT 
                Appointment.BookingReference,
                Appointment.Date,
                TimeSlot.StartTime,
                TimeSlot.EndTime,
                Barber.FirstName AS BarberFirstName,
                Barber.LastName AS BarberLastName
            FROM tblAppointment AS Appointment
            JOIN tblAppointmentSlots AS AppointmentSlot 
              ON Appointment.BookingReference = AppointmentSlot.BookingReference
            JOIN tblTimeSlot AS TimeSlot 
              ON AppointmentSlot.SlotID = TimeSlot.SlotID
            JOIN tblBarber AS Barber 
              ON Appointment.BarberID = Barber.BarberID
            WHERE Appointment.CustomerID = ?
            ORDER BY Appointment.Date, TimeSlot.StartTime
        """, (customerID,)).fetchall()

        # Gets services for each appointment
        serviceRows = cursor.execute("""
            SELECT 
                AppointmentService.BookingReference,
                Service.ServiceName,
                Service.Price
            FROM tblAppointmentServices AS AppointmentService
            JOIN tblService AS Service 
              ON AppointmentService.ServiceID = Service.ServiceID
            JOIN tblAppointment AS Appointment 
              ON AppointmentService.BookingReference = Appointment.BookingReference
            WHERE Appointment.CustomerID = ?
        """, (customerID,)).fetchall()

        # Groups services by booking reference
        servicesByBooking = {}
        for row in serviceRows:
            bookingRef = row["BookingReference"]
            if bookingRef not in servicesByBooking:
                servicesByBooking[bookingRef] = {
                    "services": [],
                    "totalPrice": 5.00  # £5.00 booking fee
                }
            servicesByBooking[bookingRef]["services"].append(userFriendlyServiceNames(row["ServiceName"]))
            servicesByBooking[bookingRef]["totalPrice"] += row["Price"]

        # Groups slot rows by booking reference
        slotsByBooking = {}
        for row in appointmentRows:
            bookingRef = row["BookingReference"]
            if bookingRef not in slotsByBooking:
                slotsByBooking[bookingRef] = []
            slotsByBooking[bookingRef].append(row)

        appointments = {}
        now = datetime.now()

        for bookingRef, slotRows in slotsByBooking.items():
            firstRow = slotRows[0]
            latestEndTime = max(row["EndTime"] for row in slotRows)

            try:
                appointmentDateTime = datetime.strptime(
                    f"{firstRow['Date']} {firstRow['StartTime']}", "%d-%m-%Y %H:%M"
                )
            except ValueError:
                appointmentDateTime = datetime.strptime(firstRow["Date"], "%d-%m-%Y")

            if appointmentDateTime >= now:
                appointments[bookingRef] = {
                    "bookingReference": bookingRef,
                    "date": firstRow["Date"],
                    "startTime": firstRow["StartTime"],
                    "endTime": latestEndTime,
                    "barberName": f"{firstRow['BarberFirstName']} {firstRow['BarberLastName']}",
                    "totalPrice": servicesByBooking.get(bookingRef, {}).get("totalPrice", 0),
                    "services": servicesByBooking.get(bookingRef, {}).get("services", [])
                }

        return list(appointments.values())

    except sqlite3.Error as error:
        print("Database error:", error)
        return []

    finally:
        conn.close()


# Parameterised SQL Statements for Customers


def getCurrentWeekCommencing():
    today = date.today()
    # Sunday week start: (weekday + 1) % 7 gives days since Sunday
    return today - timedelta(days=(today.weekday() + 1) % 7)


def getWeekCommencingStrings():
    wk = getCurrentWeekCommencing()
    return wk.strftime("%Y-%m-%d"), wk.strftime("%d-%m-%Y")


def getTimeSlotsForWeek(weekCommencingStr: str):
    conn = getDbConnection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        rows = cursor.execute("""
            SELECT *
            FROM tblTimeSlot
            WHERE WeekCommencing = ?
            ORDER BY Day, StartTime
        """, (weekCommencingStr,)).fetchall()
        return rows
    except:
        print("Database error in getTimeSlotsForWeek")
        return []
    finally:
        conn.close()


def createCustomer(firstName, middleName, lastName, email, hashedPassword, phoneNumber):
    # Inserts a new customer record using parameterized query
    # The ? placeholders prevent SQL injection attacks
    conn = getDbConnection()
    cursor = conn.cursor()
    cursor.execute("""
                   INSERT INTO tblCustomer (FirstName, MiddleName, LastName, EmailAddress, HashedPassword, IsBlackListed, PhoneNumber)
                   VALUES (?, ?, ?, ?, ?, 0, ?)""",
                   (firstName, middleName, lastName, email, hashedPassword, phoneNumber))
    conn.commit()
    customerId = cursor.lastrowid
    conn.close()
    return customerId


def getCustomerByEmail(email):
    # Retrieves customer by email using parameterized query
    # Returns None if not found, otherwise returns a dictionary-like row
    conn = getDbConnection()
    cursor = conn.cursor()
    cursor.execute("SELECT * "
                       "FROM tblCustomer "
                       "WHERE EmailAddress = ?",
                       (email,))
    customer = cursor.fetchone()
    conn.close()
    return customer


def getCustomerByPhone(phoneNumber):
    # Retrieves customer by phone number
    conn = getDbConnection()
    cursor = conn.cursor()
    cursor.execute("SELECT * "
                       "FROM tblCustomer "
                       "WHERE PhoneNumber = ?",
                       (phoneNumber,))
    customer = cursor.fetchone()
    conn.close()
    return customer


def getCustomerById(customerId):
    # Used by Flask-Login to reload user from session
    conn = getDbConnection()
    cursor = conn.cursor()
    cursor.execute("SELECT * "
                       "FROM tblCustomer "
                       "WHERE CustomerID = ?",
                       (customerId,))
    customer = cursor.fetchone()
    conn.close()
    return customer


def updateCustomerPassword(email, newHashedPassword):
    # Updates customer password using parameterized UPDATE
    conn = getDbConnection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tblCustomer "
                       "SET HashedPassword = ? "
                       "WHERE EmailAddress = ?",
                       (newHashedPassword, email))
    conn.commit()
    conn.close()


def fetchServices():
    conn = getDbConnection()
    cursor = conn.cursor()
    cursor.execute("SELECT ServiceID, ServiceName, Duration, Price, ServiceCategory FROM tblService")
    rows = cursor.fetchall()
    conn.close()

    servicesByCategory = {}
    for serviceId, serviceName, duration, price, category in rows:
        readableCategory = userFriendlyCategoryNames(category)
        readableName = userFriendlyServiceNames(serviceName)

        if readableCategory not in servicesByCategory:
            servicesByCategory[readableCategory] = []

        servicesByCategory[readableCategory].append({
            "serviceId": serviceId,
            "serviceName": readableName,
            "duration": duration,
            "price": price
        })

    return servicesByCategory


def getSelectedServicesFromIds(ids):
    if not ids:
        return []
    conn = getDbConnection()
    cursor = conn.cursor()

    ids = tuple(int(i) for i in ids)

    placeholders = ",".join("?" for _ in ids)
    query = f"""
        SELECT ServiceID, ServiceName, Duration, Price
        FROM tblService
        WHERE ServiceID IN ({placeholders})
    """
    cursor.execute(query, ids)
    rows = cursor.fetchall()
    conn.close()

    return [{
        "serviceId": row["ServiceID"],
        "serviceName": userFriendlyServiceNames(row["ServiceName"]),
        "duration": row["Duration"],
        "price": row["Price"],
    } for row in rows]


def updateSlotAvailability(cursor, appointment):
    slotIds = appointment.getSlotIds()
    cursor.executemany("""
        UPDATE tblTimeSlot
        SET IsAvailable = 0
        WHERE SlotID = ?
    """, [(sid,) for sid in slotIds])

# Parameterised SQL Statements for Barbers


def insertBarbers():
    barbers = [
        (1, "Fayaz", "Gani", "adminfayaz@email.com", "1d2129c27a88edd6532254aa2397a14f889b5d139f20697d7a0a40b88861f210", 1, 11),
        (2, "Moosa", "Gani", "barbermoosa@email.com", "6597e230212f0af1f3a0537fd39634a59b2f22d335dce4c0fe6c3ce7928762f7", 0, 7),
        (3, "Uwais", "Gani", "barberuwais@email.com", "6e75968c94e989d4bba8164cfae98a517163f47a8ec5c45e021c1cfe98e8158b", 0, 3)
    ]

    conn = getDbConnection()
    cursor = conn.cursor()

    cursor.executemany("""
        INSERT OR IGNORE INTO tblBarber (BarberID, FirstName, LastName, EmailAddress, HashedPassword, IsAdmin, YearsOfExperience)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, barbers)

    conn.commit()
    conn.close()


def calculateEndTime(startTime: str, durationMinutes: int):
    startDt = datetime.strptime(startTime, "%H:%M")
    endDt = startDt + timedelta(minutes = durationMinutes)
    return endDt.strftime("%H:%M")


def setSlotAvailability(slotId: int, available: bool):
    conn = getDbConnection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE tblTimeSlot
            SET IsAvailable = ?
            WHERE SlotID = ?
        """, (1 if available else 0, slotId))
        conn.commit()
    except:
        print("Database error in setSlotAvailability")
    finally:
        conn.close()


def checkIfSlotsExist(weekCommencingStr: str):
    conn = getDbConnection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        result = cursor.execute(
            "SELECT COUNT(*) AS cnt FROM tblTimeSlot WHERE WeekCommencing = ?",
            (weekCommencingStr,)
        ).fetchone()
        return result["cnt"] > 0
    except Exception as e:
        print("Database error in checkIfSlotsExist:", e)
        return False
    finally:
        conn.close()


def ensureCurrentWeekSlots():
    weekCommencingStr, _ = getWeekCommencingStrings()

    if checkIfSlotsExist(weekCommencingStr):
        return  # slots already seeded

    conn = getDbConnection()
    cursor = conn.cursor()

    for barber in getAllBarbers():
        for day in ["Tue", "Wed", "Thu", "Fri", "Sat"]:
            for hour in range(10, 18):
                for minute in (0, 20, 40):
                    startTime = f"{hour:02d}:{minute:02d}"
                    endTime = calculateEndTime(startTime, 20)

                    cursor.execute("""
                        INSERT INTO tblTimeSlot (Day, StartTime, EndTime, WeekCommencing, IsAvailable, BarberID)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (day, startTime, endTime, weekCommencingStr, 1, barber["BarberID"]))

    conn.commit()
    conn.close()


def generateWeeklySlots():
    conn = getDbConnection()
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(WeekCommencing) FROM tblTimeSlot")
    latestWeek = cursor.fetchone()[0]

    today = datetime.today()
    nextSunday = today + timedelta(days=(6 - today.weekday()))
    weekCommencing = nextSunday.strftime("%Y-%m-%d")

    if latestWeek is None or latestWeek < weekCommencing:
        barberIds = cursor.execute("SELECT BarberID FROM tblBarber").fetchall()
        days = ["Tue", "Wed", "Thu", "Fri", "Sat"]
        startHour = 10
        endHour = 18
        slotLength = 20

        for barber in barberIds:
            barberId = barber[0]
            for day in days:
                currentTime = datetime.strptime("10:00", "%H:%M")
                endTime = datetime.strptime("18:00", "%H:%M")

                while currentTime < endTime:
                    startStr = currentTime.strftime("%H:%M")
                    endStr = (currentTime + timedelta(minutes = slotLength)).strftime("%H:%M")

                    cursor.execute("""
                        INSERT INTO tblTimeSlot (Day, StartTime, EndTime, WeekCommencing, IsAvailable, BarberID)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (day, startStr, endStr, weekCommencing, True, barberId))

                    currentTime += timedelta(minutes = slotLength)

        conn.commit()
    conn.close()


def getAllTimeSlots():
    conn = getDbConnection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tblTimeSlot")
    rows = cursor.fetchall()
    conn.close()
    return rows


def getBarberByEmail(email):
    conn = getDbConnection()
    cursor = conn.cursor()
    cursor.execute("SELECT * "
                       "FROM tblBarber "
                       "WHERE EmailAddress = ?",
                       (email,))
    barber = cursor.fetchone()
    conn.close()
    return barber


def getBarberById(barberId):
    conn = getDbConnection()
    cursor = conn.cursor()
    cursor.execute("SELECT * "
                       "FROM tblBarber "
                       "WHERE BarberID = ?",
                       (barberId,))
    barber = cursor.fetchone()
    conn.close()
    return barber


def getAllBarbers():
    conn = getDbConnection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT BarberID, FirstName, LastName, YearsOfExperience
        FROM tblBarber
    """)
    rows = cursor.fetchall()
    conn.close()

    # Converts rows into list of dictionaries
    barbers = []
    for row in rows:
        barbers.append({
            "BarberID": row[0],
            "FirstName": row[1],
            "LastName": row[2],
            "YearsOfExperience": row[3]
        })

    for row in rows:
        print(row)

    return barbers


def updateBarberPassword(email, newHashedPassword):
    conn = getDbConnection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tblBarber "
                       "SET HashedPassword = ? "
                       "WHERE EmailAddress = ?",
                       (newHashedPassword, email))
    conn.commit()
    conn.close()


def getRevenueDataForWeek(barberID: int, weekCommencing: str):
    conn = getDbConnection()
    cursor = conn.cursor()
    print("WEEK COMMENCING VALUES:")
    cursor.execute("SELECT DISTINCT WeekCommencing FROM tblTimeSlot")
    for row in cursor.fetchall():
        print(row[0])
    try:
        rows = cursor.execute("""
            SELECT
                Appointment.BookingReference,
                TimeSlot.Day,
                SUM(DISTINCT Service.Price) AS TotalPrice
            FROM tblAppointment AS Appointment
            JOIN tblAppointmentSlots AS AppointmentSlot
              ON Appointment.BookingReference = AppointmentSlot.BookingReference
            JOIN tblTimeSlot AS TimeSlot
              ON AppointmentSlot.SlotID = TimeSlot.SlotID
            JOIN tblAppointmentServices AS AppointmentService
              ON Appointment.BookingReference = AppointmentService.BookingReference
            JOIN tblService AS Service
              ON AppointmentService.ServiceID = Service.ServiceID
            WHERE Appointment.BarberID = ?
              AND TimeSlot.WeekCommencing = ?
            GROUP BY Appointment.BookingReference, TimeSlot.Day;
        """, (barberID, weekCommencing)).fetchall()
        return rows
    except:
        print("Database error")
        return []

    finally:
        conn.close()

def getScheduleForWeek(barberID: int, weekCommencing: str):
    conn = getDbConnection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        rows = cursor.execute("""
            SELECT
                tblAppointment.BookingReference,
                tblAppointment.Date,
                tblTimeSlot.Day,
                MIN(tblTimeSlot.StartTime) AS StartTime,
                MAX(tblTimeSlot.EndTime) AS EndTime,
                tblCustomer.FirstName,
                tblCustomer.LastName,
                tblAppointment.NoteForBarber,
                serviceSummary.TotalPrice,
                serviceSummary.Services,
                serviceSummary.Categories
            FROM tblAppointment
            JOIN tblAppointmentSlots
              ON tblAppointment.BookingReference = tblAppointmentSlots.BookingReference
            JOIN tblTimeSlot
              ON tblAppointmentSlots.SlotID = tblTimeSlot.SlotID
            JOIN tblCustomer
              ON tblAppointment.CustomerID = tblCustomer.CustomerID
            LEFT JOIN (
                SELECT
                    tblAppointmentServices.BookingReference,
                    SUM(tblService.Price) AS TotalPrice,
                    GROUP_CONCAT(tblService.ServiceName, ", ") AS Services,
                    GROUP_CONCAT(tblService.ServiceCategory, ", ") AS Categories
                FROM tblAppointmentServices
                JOIN tblService
                  ON tblAppointmentServices.ServiceID = tblService.ServiceID
                GROUP BY tblAppointmentServices.BookingReference
            ) AS serviceSummary
              ON serviceSummary.BookingReference = tblAppointment.BookingReference
            WHERE tblAppointment.BarberID = ?
              AND tblTimeSlot.WeekCommencing = ?
            GROUP BY
                tblAppointment.BookingReference,
                tblAppointment.Date,
                tblTimeSlot.Day,
                tblCustomer.FirstName,
                tblCustomer.LastName
            ORDER BY tblAppointment.Date, StartTime
        """, (barberID, weekCommencing)).fetchall()

        return rows

    except:
        print("Database error")
        return []
    finally:
        conn.close()


def getBookedSlotIdsForWeek(weekCommencingStr: str) -> set:
    conn = getDbConnection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        rows = cursor.execute("""
            SELECT tblTimeSlot.SlotID
            FROM tblTimeSlot
            INNER JOIN tblAppointmentSlots ON tblTimeSlot.SlotID = tblAppointmentSlots.SlotID
            WHERE tblTimeSlot.WeekCommencing = ?
        """, (weekCommencingStr,)).fetchall()

        bookedSlotIds = {row["SlotID"] for row in rows}
        return bookedSlotIds
    except:
        print("Database error in getBookedSlotIdsForWeek")
        return set()
    finally:
        conn.close()


def getCustomerEmailByBookingRef(bookingRef: int):
    conn = getDbConnection()
    cursor = conn.cursor()

    try:
        result = cursor.execute("""
            SELECT tblCustomer.EmailAddress
            FROM tblAppointment
            JOIN tblCustomer ON tblAppointment.CustomerID = tblCustomer.CustomerID
            WHERE tblAppointment.BookingReference = ?
        """, (bookingRef,)).fetchone()

        return result["EmailAddress"] if result else None
    except:
        print("Database error")
        return None
    finally:
        conn.close()


def cancelAppointmentByBookingRef(bookingRef: int):
    conn = getDbConnection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE tblTimeSlot
            SET IsAvailable = 1
            WHERE SlotID IN (
                SELECT SlotID
                FROM tblAppointmentSlots
                WHERE BookingReference = ?
            )
        """, (bookingRef,))

        cursor.execute("DELETE FROM tblAppointmentServices WHERE BookingReference = ?", (bookingRef,))
        cursor.execute("DELETE FROM tblAppointmentSlots WHERE BookingReference = ?", (bookingRef,))
        cursor.execute("DELETE FROM tblAppointment WHERE BookingReference = ?", (bookingRef,))
        affected = cursor.rowcount

        conn.commit()
        return affected > 0 # Returns true if rows were deleted from tblAppointment

    except:
        print("Database error in cancelAppointmentByBookingRef")
        return False

    finally:
        conn.close()


def getAllCustomers():
    conn = getDbConnection()
    cursor = conn.cursor()
    try:
        rows = cursor.execute("""
            SELECT CustomerID, FirstName, MiddleName, LastName, EmailAddress, IsBlackListed
            FROM tblCustomer
            ORDER BY CustomerID
        """).fetchall()
        return rows
    finally:
        conn.close()


def getBlacklistedCustomers():
    conn = getDbConnection()
    cursor = conn.cursor()
    try:
        rows = cursor.execute("""
            SELECT CustomerID, FirstName, MiddleName, LastName, EmailAddress, IsBlackListed
            FROM tblCustomer
            WHERE IsBlackListed = 1
            ORDER BY CustomerID
        """).fetchall()
        return rows
    finally:
        conn.close()


def customerExists(customerId: int) -> bool:
    conn = getDbConnection()
    cursor = conn.cursor()
    try:
        result = cursor.execute("""
            SELECT 1 FROM tblCustomer WHERE CustomerID = ?
        """, (customerId,)).fetchone()
        return result is not None
    finally:
        conn.close()


def addCustomerToBlacklist(customerId: int) -> bool:
    if not customerExists(customerId):
        return False
    conn = getDbConnection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tblCustomer
        SET IsBlackListed = 1
        WHERE CustomerID = ?
    """, (customerId,))
    conn.commit()
    conn.close()
    return True

def removeCustomerFromBlacklist(customerId: int) -> bool:
    if not customerExists(customerId):
        return False
    conn = getDbConnection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tblCustomer
        SET IsBlackListed = 0
        WHERE CustomerID = ?
    """, (customerId,))
    conn.commit()
    conn.close()
    return True


# Unverified User SQL Statements

def createUnverified(firstName, middleName, lastName, email, hashedPassword, phoneNumber, verificationCode,
                      isPasswordReset):
    # Creates temporary unverified record for email verification or password reset
    conn = getDbConnection()
    cursor = conn.cursor()
    cursor.execute("""
                   INSERT INTO tblUnverified (FirstName, MiddleName, LastName, EmailAddress, HashedPassword, PhoneNumber, VerificationCode, IsPasswordReset)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                   (firstName, middleName, lastName, email, hashedPassword, phoneNumber, verificationCode, isPasswordReset))
    conn.commit()
    unverifiedId = cursor.lastrowid
    conn.close()
    return unverifiedId


def getUnverifiedById(unverifiedId, isPasswordReset=None):
    conn = getDbConnection()
    cursor = conn.cursor()
    if isPasswordReset is not None:
        cursor.execute("SELECT * "
                           "FROM tblUnverified "
                           "WHERE UnverifiedID = ? "
                           "AND IsPasswordReset = ?",
                           (unverifiedId, isPasswordReset))
    else:
        cursor.execute("SELECT * "
                           "FROM tblUnverified "
                           "WHERE UnverifiedID = ?",
                            (unverifiedId,))
    unverified = cursor.fetchone()
    conn.close()
    return unverified


def deleteUnverified(unverifiedId):
    # Deletes unverified record after successful verification
    conn = getDbConnection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tblUnverified "
                       "WHERE UnverifiedID = ?",
                       (unverifiedId,))
    conn.commit()
    conn.close()


def cleanupExpiredUnverified(expiryMinutes=30):
    # Removes unverified records older than specified time
    # Uses SQLite's datetime functions with parameterized query
    conn = getDbConnection()
    cursor = conn.cursor()
    cursor.execute("""
                       DELETE
                       FROM tblUnverified
                       WHERE datetime(CodeCreatedAt) < datetime('now', '-' || ? || ' minutes')""", # Current time minus expiryMinutes
                    (expiryMinutes,))
    deletedCount = cursor.rowcount
    conn.commit()
    conn.close()
    return deletedCount
