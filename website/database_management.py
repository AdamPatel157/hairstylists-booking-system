import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "database.db")

def get_db_connection():
    # Creates a connection to the SQLite database
    # row_factory makes results accessible like dictionaries (e.g., row['EmailAddress'])
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    # Creates all required tables if they don't exist
    # This replaces SQLAlchemy's db.create_all()
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
                       0
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
                       ServiceID       INTEGER PRIMARY KEY AUTOINCREMENT,
                       ServiceName     TEXT    NOT NULL,
                       Duration        INTEGER NOT NULL,
                       Price           REAL    NOT NULL,
                       ServiceCategory TEXT    NOT NULL
                   )
                   """)

    # TimeSlot table - stores barber availability slots
    # Contains day, time range, and availability status
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS tblTimeSlot
                   (
                       SlotID         INTEGER PRIMARY KEY AUTOINCREMENT,
                       Day            TEXT    NOT NULL,
                       StartTime      TEXT    NOT NULL,
                       EndTime        TEXT    NOT NULL,
                       WeekCommencing TEXT    NOT NULL,
                       IsAvailable    INTEGER DEFAULT 1,
                       BarberID       INTEGER NOT NULL,
                       FOREIGN KEY (BarberID) REFERENCES tblBarber (BarberID)
                   )
                   """)

    # Appointment table - stores customer bookings
    # Links customers to barbers with booking date and notes
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS tblAppointment
                   (
                       BookingReference INTEGER PRIMARY KEY AUTOINCREMENT,
                       Date             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       NoteForBarber    TEXT,
                       BarberID         INTEGER NOT NULL,
                       CustomerID       INTEGER NOT NULL,
                       FOREIGN KEY (BarberID) REFERENCES tblBarber (BarberID),
                       FOREIGN KEY (CustomerID) REFERENCES tblCustomer (CustomerID)
                   )
                   """)

    # AppointmentSlots table - junction table linking appointments to time slots
    # Composite primary key (SlotID, BookingReference)
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS tblAppointmentSlots
                   (
                       SlotID           INTEGER NOT NULL,
                       BookingReference INTEGER NOT NULL,
                       PRIMARY KEY (SlotID, BookingReference),
                       FOREIGN KEY (SlotID) REFERENCES tblTimeSlot (SlotID),
                       FOREIGN KEY (BookingReference) REFERENCES tblAppointment (BookingReference)
                   )
                   """)

    # AppointmentServices table - junction table linking appointments to services
    # Allows multiple services per appointment (many-to-many relationship)
    # Composite primary key (ServiceID, BookingReference)
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS tblAppointmentServices
                   (
                       ServiceID        INTEGER NOT NULL,
                       BookingReference INTEGER NOT NULL,
                       PRIMARY KEY (ServiceID, BookingReference),
                       FOREIGN KEY (ServiceID) REFERENCES tblService (ServiceID),
                       FOREIGN KEY (BookingReference) REFERENCES tblAppointment (BookingReference)
                   )
                   """)

    conn.commit()
    conn.close()


# CUSTOMER OPERATIONS - All use parameterized queries (?) for security

def create_customer(firstName, middleName, lastName, email, hashedPassword, phoneNumber):
    # Inserts a new customer record using parameterized query
    # The ? placeholders prevent SQL injection attacks
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   INSERT INTO tblCustomer (FirstName, MiddleName, LastName, EmailAddress, HashedPassword, IsBlackListed, PhoneNumber)
                   VALUES (?, ?, ?, ?, ?, 0, ?)
                   """, (firstName, middleName, lastName, email, hashedPassword, phoneNumber))
    conn.commit()
    customerId = cursor.lastrowid
    conn.close()
    return customerId


def get_customer_by_email(email):
    # Retrieves customer by email using parameterized query
    # Returns None if not found, otherwise returns a dictionary-like row
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tblCustomer WHERE EmailAddress = ?', (email,))
    customer = cursor.fetchone()
    conn.close()
    return customer


def get_customer_by_phone(phoneNumber):
    # Retrieves customer by phone number
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tblCustomer WHERE PhoneNumber = ?', (phoneNumber,))
    customer = cursor.fetchone()
    conn.close()
    return customer


def get_customer_by_id(customerId):
    # Used by Flask-Login to reload user from session
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tblCustomer WHERE CustomerID = ?', (customerId,))
    customer = cursor.fetchone()
    conn.close()
    return customer


def update_customer_password(email, newHashedPassword):
    # Updates customer password using parameterized UPDATE
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE tblCustomer SET HashedPassword = ? WHERE EmailAddress = ?',
                   (newHashedPassword, email))
    conn.commit()
    conn.close()


# BARBER OPERATIONS

def get_barber_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tblBarber WHERE EmailAddress = ?', (email,))
    barber = cursor.fetchone()
    conn.close()
    return barber


def get_barber_by_id(barberId):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tblBarber WHERE BarberID = ?', (barberId,))
    barber = cursor.fetchone()
    conn.close()
    return barber


def update_barber_password(email, newHashedPassword):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE tblBarber SET HashedPassword = ? WHERE EmailAddress = ?',
                   (newHashedPassword, email))
    conn.commit()
    conn.close()


# UNVERIFIED USER OPERATIONS

def create_unverified(firstName, middleName, lastName, email, hashedPassword, phoneNumber, verificationCode,
                      isPasswordReset):
    # Creates temporary unverified record for email verification or password reset
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   INSERT INTO tblUnverified (FirstName, MiddleName, LastName, EmailAddress, HashedPassword, PhoneNumber, VerificationCode, IsPasswordReset)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                   """, (firstName, middleName, lastName, email, hashedPassword, phoneNumber, verificationCode,
                         isPasswordReset))
    conn.commit()
    unverifiedId = cursor.lastrowid
    conn.close()
    return unverifiedId

def get_unverified_by_id(unverifiedId, isPasswordReset=None):
    # Retrieves unverified record, optionally filtered by reset status
    conn = get_db_connection()
    cursor = conn.cursor()
    if isPasswordReset is not None:
        cursor.execute('SELECT * FROM tblUnverified WHERE UnverifiedID = ? AND IsPasswordReset = ?',
                       (unverifiedId, isPasswordReset))
    else:
        cursor.execute('SELECT * FROM tblUnverified WHERE UnverifiedID = ?', (unverifiedId,))
    unverified = cursor.fetchone()
    conn.close()
    return unverified

def delete_unverified(unverifiedId):
    # Deletes unverified record after successful verification
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tblUnverified WHERE UnverifiedID = ?', (unverifiedId,))
    conn.commit()
    conn.close()

def cleanup_expired_unverified(expiryMinutes=30):
    # Removes unverified records older than specified time
    # Uses SQLite's datetime functions with parameterized query
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
                   DELETE
                   FROM tblUnverified
                   WHERE datetime(CodeCreatedAt) < datetime('now', '-' || ? || ' minutes')
                   ''', (expiryMinutes,))
    deletedCount = cursor.rowcount
    conn.commit()
    conn.close()
    return deletedCount