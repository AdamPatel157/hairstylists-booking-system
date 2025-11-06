from flask import Blueprint, render_template, request, flash, redirect
# 'Blueprint' library allows different sections of a Flask application to be organised into separate modules.
# 'render_template' library allows HTML templates to be displayed dynamically through Python code.
# 'request' library allows data to be accessed from incoming HTTP requests, such as form submissions.
# 'flash' library allows for the system to display temporary feedback messages to the user's screen.
# 'redirect' library allows the system to automatically navigate the user to a different webpage or route.

from .models import tblCustomer, tblBarber
# Allows the system to add new records to tblCustomer by accessing its class in models.py

from . import db

from algorithms.hash_password import hash_password
# Imports the SHA-256 hashing algorithm for passwords from the hash_password file

user_redirection = Blueprint("auth", __name__)

# Registration Validation Functions
# If validation test for field passes, returns True
# If validation test for field fails, returns False and displays error message
# All functions must return True for registration to be successful

def validateName(name, namePos):
    lowercaseEnglishAlphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    if len(name) < 2:
        flash(f"{namePos} Name must be greater than 1 character long.", category="Error")
        return False
    elif any(character.lower() not in lowercaseEnglishAlphabet for character in name):
        flash(f"{namePos} Name can only contain English alphabet characters.", category="Error")
        return False
    else:
        return True

def validateEmail(emailAddress):
    if len(emailAddress) < 4:
        flash("Length of Email must be greater than 3 characters long.", category="Error")
        return False
    elif '@' not in list(emailAddress):
        flash("Email must contain '@' symbol.", category="Error")
        return False
    elif '.' not in list(emailAddress):
        flash("Email must contain '.' symbol.", category="Error")
        return False
    else:
        return True

def validatePhoneNumber(phoneNum):
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    if len(phoneNum) != 11:
        flash("Phone Numbers must be exactly 11 characters long.", category="Error")
        return False
    else:
        for character in phoneNum:
            if character not in numbers:
                flash("Phone Numbers can only contain integer numbers 0-9.", category="Error")
                return False
        if phoneNum[0] != '0':
            flash("Phone Numbers must begin with the number '0'.", category="Error")
            return False
        else:
            return True

def validatePassword(createPassword, confirmPassword):
    passwordPunctuation = ['?', '!', '£', '%', '^', '&', '*', '(', ')', '/', '#']
    lowercaseEnglishAlphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    if len(createPassword) < 8:
        flash("Passwords must be at least 8 characters in length.", category="Error")
        return False

    elif not any(character.lower() in lowercaseEnglishAlphabet for character in createPassword):
        flash("Passwords must contain at least one English alphabet character.", category="Error")
        return False

    elif not any(character in numbers for character in createPassword):
        flash("Passwords must contain at least one integer number 0-9.", category="Error")
        return False

    elif not any(character in passwordPunctuation for character in createPassword):
        flash("Passwords must contain at least one punctuation character from ['?', '!', '£', '%', '^', '&', '*', '(', ')', '/', '#'].", category="Error")
        return False

    elif createPassword == createPassword.lower():  # If there are no uppercase letters
        flash("Passwords must contain at least one uppercase letter.", category="Error")
        return False

    elif createPassword == createPassword.upper():  # If there are no lowercase letters
        flash("Passwords must contain at least one lowercase letter.", category="Error")
        return False

    elif createPassword != confirmPassword:  # If the confirmation password does not equal the created password
        flash("Passwords do not match.", category="Error")
        return False

    else:
        return True

# Processes webpage HTTP requests

@user_redirection.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST": # Evaluates the below block if receiving a POST request from the login.html webpage
        # Assigns received user input values from HTTP POST Request to local variables with matching identifiers
        email = request.form.get("email").strip()
        password = request.form.get("password")

        customer = tblCustomer.query.filter_by(EmailAddress=email).first()
        barber = tblBarber.query.filter_by(EmailAddress=email).first()

        if customer:
            if customer.HashedPassword == hash_password(password):
                flash("You have successfully logged in and been taken to the customer dashboard", category="Success")
                return redirect("/") # Link to customer dashboard
            else:
                flash("Incorrect Password. Please try again.", category="Error")
        elif barber:
            if barber.HashedPassword == hash_password(password):
                flash("You have successfully logged in and been taken to the barber dashboard", category="Success")
                return redirect("/") # Link to barber dashboard
            else:
                flash("Incorrect Password. Please try again.", category="Error")
        else:
            flash("Incorrect Email Address. Please try again, or create an account with that email.", category="Error")

    return render_template("webpages/user_management/login.html")

@user_redirection.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST": # Evaluates the below block if receiving a POST request from the register.html webpage
        # Assigns received user input values from HTTP POST Request to local variables with matching identifiers
        firstName = request.form.get("firstName").strip()
        middleName = request.form.get("middleName").strip()
        lastName = request.form.get("lastName").strip()
        email = request.form.get("email").strip()
        phoneNumber = request.form.get("phoneNumber").strip()
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        # Passes form inputs into registration validation procedures
        # The procedures return True if passes validation and False if it fails
        firstNameIsValidated = validateName(firstName, "First")
        middleNameIsValidated = validateName(middleName, "Middle")
        lastNameIsValidated = validateName(lastName, "Last")
        emailIsValidated = validateEmail(email)
        phoneNumberIsValidated = validatePhoneNumber(phoneNumber)
        passwordIsValidated = validatePassword(password1, password2)

        # If all validation check procedures are true, proceeds
        if firstNameIsValidated and middleNameIsValidated and lastNameIsValidated and emailIsValidated and phoneNumberIsValidated and passwordIsValidated:
            hashedPassword = hash_password(password1)
            # noinspection PyArgumentList
            newCustomer = tblCustomer(FirstName=firstName, MiddleName=middleName, LastName = lastName, EmailAddress=email, HashedPassword=hashedPassword, IsBlackListed=False, PhoneNumber=phoneNumber)
            db.session.add(newCustomer) # Adds the user's data to tblCustomer
            db.session.commit()
            flash("Account Successfully Created.", category = "Success")
            return redirect("/login")

    return render_template("webpages/user_management/register.html")

@user_redirection.route("/logout")
def logout():
    flash("You have logged out and been returned to the home page.", category="Success")
    return redirect("/")