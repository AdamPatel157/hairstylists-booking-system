# Creates the abstract 'User' superclass
class User:

    # Initialises the attributes for the 'User' superclass
    def __init__(self, firstName, lastName, emailAddress, hashedPassword):
        self.firstName = firstName
        self.lastname = lastName
        self.emailAddress = emailAddress
        self.hashedPassword = hashedPassword

    def login(self):
        pass

    def logout(self):
        pass

from flask_login import UserMixin

class Customer(UserMixin):
    # Represents a logged-in customer user
    # UserMixin provides default implementations for Flask-Login methods
    def __init__(self, customerId, firstName, middleName, lastName, email, hashedPassword, isBlacklisted, phoneNumber):
        self.customerId = customerId
        self.firstName = firstName
        self.middleName = middleName
        self.lastName = lastName
        self.email = email
        self.hashedPassword = hashedPassword
        self.isBlacklisted = isBlacklisted
        self.phoneNumber = phoneNumber

    def get_id(self):
        # Flask-Login uses this to store user ID in session
        # Prefix distinguishes customers from barbers
        return f"customer_{self.customerId}"

class Barber(UserMixin):
    # Represents a logged-in barber/admin user
    def __init__(self, barberId, firstName, middleName, lastName, email, hashedPassword, isAdmin):
        self.barberId = barberId
        self.firstName = firstName
        self.middleName = middleName
        self.lastName = lastName
        self.email = email
        self.hashedPassword = hashedPassword
        self.isAdmin = isAdmin

    def get_id(self):
        return f"barber_{self.barberId}"

    def viewSchedule(self):
        pass

    def exportSchedule(self):
        pass

    def blockTimeSlots(self):
        pass

    def viewBasicRevenue(self):
        pass

# Creates the 'Admin' subclass inheriting from the 'Barber' superclass
class Admin(Barber):

    def cancelAppointment(self):
        pass

    def blacklistCustomer(self):
        pass

    def viewComprehensiveRevenue(self):
        pass