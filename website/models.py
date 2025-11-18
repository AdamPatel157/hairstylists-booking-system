from . import db
# Imports the 'db' object from the 'website' directory

from flask_login import UserMixin

from sqlalchemy.sql import func
# Gets current date/ time to store in database record

# Sets up SQL tables through classes

# noinspection PyPep8Naming
class tblCustomer(db.Model, UserMixin):
    __tablename__ = "tblCustomer"
    CustomerID = db.Column(db.Integer, primary_key=True, nullable=False)
    FirstName = db.Column(db.String(50), nullable=False)
    MiddleName = db.Column(db.String(50), nullable=True)
    LastName = db.Column(db.String(50), nullable=False)
    EmailAddress = db.Column(db.String(50), unique=True, nullable=False)
    HashedPassword = db.Column(db.String(64), nullable=False)
    IsBlackListed = db.Column(db.Boolean, default=False, nullable=False)
    PhoneNumber = db.Column(db.String(11), unique=True, nullable=True)

    # Allows CustomerID to be recognised by Flask login as a user ID
    def get_id(self):
        return str(self.CustomerID)

# noinspection PyPep8Naming
class tblBarber(db.Model, UserMixin):
    __tablename__ = "tblBarber"
    BarberID = db.Column(db.Integer, primary_key=True, nullable=False)
    FirstName = db.Column(db.String(50), nullable=False)
    MiddleName = db.Column(db.String(50), nullable=True)
    LastName = db.Column(db.String(50), nullable=False)
    EmailAddress = db.Column(db.String(50), unique=True, nullable=False)
    HashedPassword = db.Column(db.String(64), nullable=False)
    IsAdmin = db.Column(db.Boolean, default=False, nullable=False)
    YearsOfExperience = db.Column(db.Integer, nullable=False)

    # Allows Barber ID to be recognised by Flask login as a user ID
    def get_id(self):
        return str(self.BarberID)

# noinspection PyPep8Naming
class tblTimeSlot(db.Model):
    __tablename__ = "tblTimeSlot"
    SlotID = db.Column(db.Integer, primary_key=True, nullable=False)
    Day = db.Column(db.String(10), nullable=False)
    StartTime = db.Column(db.Time, nullable=False)
    EndTime = db.Column(db.Time, nullable=False)
    WeekCommencing = db.Column(db.DateTime, nullable=False)
    IsAvailable = db.Column(db.Boolean, default=True, nullable=False)
    BarberID = db.Column(db.Integer, db.ForeignKey('tblBarber.BarberID'), nullable=False)

# noinspection PyPep8Naming
class tblAppointment(db.Model):
    __tablename__ = "tblAppointment"
    BookingReference = db.Column(db.Integer, primary_key=True, nullable=False)
    Date = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    NoteForBarber = db.Column(db.String(10000), nullable=True)
    BarberID = db.Column(db.Integer, db.ForeignKey('tblBarber.BarberID'), nullable=False)
    CustomerID = db.Column(db.Integer, db.ForeignKey('tblCustomer.CustomerID'), nullable=False)

# noinspection PyPep8Naming
class tblService(db.Model):
    __tablename__ = "tblService"
    ServiceID = db.Column(db.Integer, primary_key=True, nullable=False)
    ServiceName = db.Column(db.String(50), nullable=False)
    Duration = db.Column(db.Integer, nullable=False)
    Price = db.Column(db.Numeric(10,2), nullable=False) # Exact Decimal Values with 2 d.p
    ServiceCategory = db.Column(db.String(50), nullable=False)

# noinspection PyPep8Naming
class tblAppointmentSlots(db.Model):
    __tablename__ = "tblAppointmentSlots"
    SlotID = db.Column(db.Integer, db.ForeignKey('tblTimeSlot.SlotID'), primary_key=True, nullable=False)
    BookingReference = db.Column(db.Integer, db.ForeignKey('tblAppointment.BookingReference'), primary_key=True, nullable=False)

# noinspection PyPep8Naming
class tblAppointmentServices(db.Model):
    __tablename__ = "tblAppointmentServices"
    ServiceID = db.Column(db.Integer, db.ForeignKey('tblService.ServiceID'), primary_key=True, nullable=False)
    BookingReference = db.Column(db.Integer, db.ForeignKey('tblAppointment.BookingReference'), primary_key=True, nullable=False)

# noinspection PyPep8Naming
class tblUnverified(db.Model):
    __tablename__ = "tblUnverified"
    UnverifiedID = db.Column(db.Integer, primary_key=True, nullable=False)
    FirstName = db.Column(db.String(50), nullable=False)
    MiddleName = db.Column(db.String(50), nullable=True)
    LastName = db.Column(db.String(50), nullable=False)
    EmailAddress = db.Column(db.String(50), nullable=False)
    HashedPassword = db.Column(db.String(64), nullable=False)
    PhoneNumber = db.Column(db.String(11), nullable=True)
    VerificationCode = db.Column(db.String(6), nullable=False)
    CodeCreatedAt = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    IsPasswordReset = db.Column(db.Boolean, default=False, nullable=False)