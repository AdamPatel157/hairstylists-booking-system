import sqlite3
import os

from website.user_friendly_names import user_friendly_service_names, user_friendly_category_names

from datetime import datetime, timedelta

databasePath = os.path.join(os.path.dirname(__file__), "database.db")

def get_db_connection():
    # Creates a connection to the SQLite database
    # row_factory makes results accessible as dictionaries
    conn = sqlite3.connect(databasePath)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# FOR TESTING -------------------------------------------------------------------

def readTimeSlots():
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM tblTimeSlot").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def readAppointments():
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM tblAppointment").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def readAppointmentServices():
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM tblAppointmentServices").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def readAppointmentSlots():
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM tblAppointmentSlots").fetchall()
    conn.close()
    return [dict(row) for row in rows]

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

def init_db():
    # Creates all required tables if they don't exist
    conn = get_db_connection()
    cursor = conn.cursor()

    # Customer table - stores registered customer accounts
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

    # Unverified table - temporary storage for email verification and password resets
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


# Parameterised SQL Statements for Customers

def create_customer(firstName, middleName, lastName, email, hashedPassword, phoneNumber):
    # Inserts a new customer record using parameterized query
    # The ? placeholders prevent SQL injection attacks
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   INSERT INTO tblCustomer (FirstName, MiddleName, LastName, EmailAddress, HashedPassword, IsBlackListed, PhoneNumber)
                   VALUES (?, ?, ?, ?, ?, 0, ?)""",
                   (firstName, middleName, lastName, email, hashedPassword, phoneNumber))
    conn.commit()
    customerId = cursor.lastrowid
    conn.close()
    return customerId


def get_customer_by_email(email):
    # Retrieves customer by email using parameterized query
    # Returns None if not found, otherwise returns a dictionary-like row
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * "
                       "FROM tblCustomer "
                       "WHERE EmailAddress = ?",
                       (email,))
    customer = cursor.fetchone()
    conn.close()
    return customer

def get_customer_by_phone(phoneNumber):
    # Retrieves customer by phone number
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * "
                       "FROM tblCustomer "
                       "WHERE PhoneNumber = ?",
                       (phoneNumber,))
    customer = cursor.fetchone()
    conn.close()
    return customer

def get_customer_by_id(customerId):
    # Used by Flask-Login to reload user from session
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * "
                       "FROM tblCustomer "
                       "WHERE CustomerID = ?",
                       (customerId,))
    customer = cursor.fetchone()
    conn.close()
    return customer

def update_customer_password(email, newHashedPassword):
    # Updates customer password using parameterized UPDATE
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tblCustomer "
                       "SET HashedPassword = ? "
                       "WHERE EmailAddress = ?",
                       (newHashedPassword, email))
    conn.commit()
    conn.close()

def fetch_services():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ServiceID, ServiceName, Duration, Price, ServiceCategory FROM tblService")
    rows = cursor.fetchall()
    conn.close()

    servicesByCategory = {}
    for serviceId, serviceName, duration, price, category in rows:
        readableCategory = user_friendly_category_names(category)
        readableName = user_friendly_service_names(serviceName)

        if readableCategory not in servicesByCategory:
            servicesByCategory[readableCategory] = []

        servicesByCategory[readableCategory].append({
            "serviceId": serviceId,
            "serviceName": readableName,
            "duration": duration,
            "price": price
        })

    return servicesByCategory

def get_selected_services_from_ids(ids):
    if not ids:
        return []
    conn = get_db_connection()
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
        "serviceName": user_friendly_service_names(row["ServiceName"]),
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

def insert_barbers():
    barbers = [
        (1, "Fayaz", "Gani", "adminfayaz@email.com", "1d2129c27a88edd6532254aa2397a14f889b5d139f20697d7a0a40b88861f210", 1, 11),
        (2, "Moosa", "Gani", "barbermoosa@email.com", "6597e230212f0af1f3a0537fd39634a59b2f22d335dce4c0fe6c3ce7928762f7", 0, 7),
        (3, "Uwais", "Gani", "barberuwais@email.com", "6e75968c94e989d4bba8164cfae98a517163f47a8ec5c45e021c1cfe98e8158b", 0, 3)
    ]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.executemany("""
        INSERT OR IGNORE INTO tblBarber (BarberID, FirstName, LastName, EmailAddress, HashedPassword, IsAdmin, YearsOfExperience)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, barbers)

    conn.commit()
    conn.close()


def ensureCurrentWeekSlots():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get the latest week commencing in the DB
    cursor.execute("SELECT MAX(WeekCommencing) FROM tblTimeSlot")
    latestWeek = cursor.fetchone()[0]
    conn.close()

    # Calculate the current week's Sunday
    today = datetime.today()
    currentSunday = today - timedelta(days=today.weekday() + 1) if today.weekday() != 6 else today
    weekCommencing = currentSunday.strftime("%Y-%m-%d")

    # If no slots exist or the latest week is older, generate new ones
    if latestWeek is None or latestWeek < weekCommencing:
        from website.database_management import generateWeeklySlots
        generateWeeklySlots()


def generateWeeklySlots():
    conn = get_db_connection()
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
                    endStr = (currentTime + timedelta(minutes=slotLength)).strftime("%H:%M")

                    cursor.execute("""
                        INSERT INTO tblTimeSlot (Day, StartTime, EndTime, WeekCommencing, IsAvailable, BarberID)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (day, startStr, endStr, weekCommencing, True, barberId))

                    currentTime += timedelta(minutes=slotLength)

        conn.commit()
    conn.close()


def getAllTimeSlots():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tblTimeSlot")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_barber_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * "
                       "FROM tblBarber "
                       "WHERE EmailAddress = ?",
                       (email,))
    barber = cursor.fetchone()
    conn.close()
    return barber


def get_barber_by_id(barberId):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * "
                       "FROM tblBarber "
                       "WHERE BarberID = ?",
                       (barberId,))
    barber = cursor.fetchone()
    conn.close()
    return barber

def getAllBarbers():
    conn = get_db_connection()
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

def update_barber_password(email, newHashedPassword):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tblBarber "
                       "SET HashedPassword = ? "
                       "WHERE EmailAddress = ?",
                       (newHashedPassword, email))
    conn.commit()
    conn.close()


# Unverified User SQL Statements

def create_unverified(firstName, middleName, lastName, email, hashedPassword, phoneNumber, verificationCode,
                      isPasswordReset):
    # Creates temporary unverified record for email verification or password reset
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   INSERT INTO tblUnverified (FirstName, MiddleName, LastName, EmailAddress, HashedPassword, PhoneNumber, VerificationCode, IsPasswordReset)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                   (firstName, middleName, lastName, email, hashedPassword, phoneNumber, verificationCode, isPasswordReset))
    conn.commit()
    unverifiedId = cursor.lastrowid
    conn.close()
    return unverifiedId

def get_unverified_by_id(unverifiedId, isPasswordReset=None):
    conn = get_db_connection()
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

def delete_unverified(unverifiedId):
    # Deletes unverified record after successful verification
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tblUnverified "
                       "WHERE UnverifiedID = ?",
                       (unverifiedId,))
    conn.commit()
    conn.close()

def cleanup_expired_unverified(expiryMinutes=30):
    # Removes unverified records older than specified time
    # Uses SQLite's datetime functions with parameterized query
    conn = get_db_connection()
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