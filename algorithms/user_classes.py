from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, firstName, lastName, emailAddress, hashedPassword):
        self.firstName = firstName
        self.lastName = lastName
        self.emailAddress = emailAddress
        self.hashedPassword = hashedPassword

    def get_id(self):
        # Abstract Method
        # Uses snake case to be recognised by Flask Login
        pass


class Customer(User):
    def __init__(self, customerId, firstName, middleName, lastName, email, hashedPassword, isBlacklisted):
        super().__init__(firstName, lastName, email, hashedPassword)
        self.customerId = customerId
        self.middleName = middleName
        self.isBlacklisted = isBlacklisted

    def get_id(self):
        # For Flask Login Recognition only
        flaskFormat = f"customer_{self.customerId}"
        return flaskFormat


    def getCustomerId(self):
        # For the ID number to be used in SQL statements
        return self.customerId


class Barber(User):
    def __init__(self, barberId, firstName, middleName, lastName, email, hashedPassword, isAdmin):
        super().__init__(firstName, lastName, email, hashedPassword)
        self.barberId = barberId
        self.middleName = middleName
        self.isAdmin = isAdmin

    def get_id(self):
        # For Flask Login Recognition only
        flaskFormat = f"barber_{self.barberId}"
        return flaskFormat

    def getBarberId(self):
        # For the ID number to be used in SQL statements
        return self.barberId

    def getIsAdminAsBoolean(self):
        return self.isAdmin == 1


class Admin(Barber):
    pass