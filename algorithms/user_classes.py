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

# Creates the 'Customer' subclass inheriting from the 'User' superclass
class Customer(User):
    def __init__(self, customerID, phoneNumber, isBlacklisted):
        self.customerID = customerID
        self.phoneNumber = phoneNumber
        self.isBlacklisted = isBlacklisted

    def createAccount(self):
        pass

    def bookAppointment(self):
        pass

    def viewAppointment(self):
        pass

# Creates the 'Barber' subclass inheriting from the 'User' superclass
class Barber(User):
    def __init__(self, barberID, yearsOfExperience, isAdmin):
        self.barberID = barberID
        self.yearsOfExperience = yearsOfExperience
        self.isAdmin = isAdmin

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