from flask import Blueprint, render_template, request, flash, redirect, session
# 'Blueprint' library allows different sections of a Flask application to be organised into separate modules.
# 'render_template' library allows HTML templates to be displayed dynamically through Python code.
# 'request' library allows data to be accessed from incoming HTTP requests, such as form submissions.
# 'flash' library allows for the system to display temporary feedback messages to the user's screen.
# 'redirect' library allows the system to automatically navigate the user to a different webpage or route.
# 'session' library allows data to be stored temporarily in cookies.

from website.database_management import (getCustomerByEmail, getBarberByEmail, createCustomer,
    getCustomerByPhone, createUnverified, getUnverifiedById,
    deleteUnverified, updateCustomerPassword, updateBarberPassword, cleanupExpiredUnverified)

from algorithms.hash_password import hashPassword

from algorithms.email_otp import generateOtp, sendVerificationEmail

from flask_login import login_user, logout_user, login_required

from algorithms.user_classes import Customer, Barber

import re
# Allows for the use of Regular Expressions

userRedirection = Blueprint("auth", __name__)

# Registration Validation Functions
# If validation test for field passes, returns True
# If validation test for field fails, returns False and displays error message
# All functions must return True for registration to be successful

def validateName(name, namePos):
    lowercaseEnglishAlphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    if (len(name) < 2) and (namePos != "Middle"): # Allows empty middle name fields
        flash(f"{namePos} Name must be greater than 1 character long.", category = "Error")
        return False
    elif any(character.lower() not in lowercaseEnglishAlphabet for character in name):
        flash(f"{namePos} Name can only contain English alphabet characters.", category = "Error")
        return False
    else:
        return True


def validateEmail(emailAddress):
    # Uses Regular Expressions to ensure that emails are of the format: 'user@example.com'
    emailPattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(emailPattern, emailAddress):
        flash("Please enter a valid email address (e.g., user@example.com).", category = "Error")
        return False
    else:
        return True

def validatePhoneNumber(phoneNum):
    if phoneNum == "":  # Allows empty phone number fields as it is optional
        return True
    else:
        # Uses Regular Expressions to ensure phone numbers are exactly 11 digits and start with 0
        phonePattern = r'^0\d{10}$'
        if not re.match(phonePattern, phoneNum):
            if not phoneNum.isdigit():
                flash("Phone Numbers can only contain digits 0-9.", category = "Error")
            elif len(phoneNum) != 11:
                flash("Phone Numbers must be exactly 11 characters long.", category = "Error")
            elif phoneNum[0] != '0':
                flash("Phone Numbers must begin with the number '0'.", category = "Error")
            else:
                flash("Please enter a valid phone number.", category = "Error")
            return False
        else:
            return True

def validatePassword(createPassword, confirmPassword):
    passwordPunctuation = ['?', '!', '£', '%', '^', '&', '*', '(', ')', '/', '#']
    lowercaseEnglishAlphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    if len(createPassword) < 8:
        flash("Passwords must be at least 8 characters in length.", category = "Error")
        return False

    elif not any(character.lower() in lowercaseEnglishAlphabet for character in createPassword):
        flash("Passwords must contain at least one English alphabet character.", category = "Error")
        return False

    elif not any(character in numbers for character in createPassword):
        flash("Passwords must contain at least one integer number 0-9.", category = "Error")
        return False

    elif not any(character in passwordPunctuation for character in createPassword):
        flash("Passwords must contain at least one punctuation character from ['?', '!', '£', '%', '^', '&', '*', '(', ')', '/', '#'].", category="Error")
        return False

    elif createPassword == createPassword.lower():  # If there are no uppercase letters
        flash("Passwords must contain at least one uppercase letter.", category = "Error")
        return False

    elif createPassword == createPassword.upper():  # If there are no lowercase letters
        flash("Passwords must contain at least one lowercase letter.", category = "Error")
        return False

    elif createPassword != confirmPassword:  # If the confirmation password does not equal the created password
        flash("Passwords do not match.", category = "Error")
        return False

    else:
        return True

# Processes webpage HTTP requests

@userRedirection.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST": # Evaluates the below block if receiving a POST request from the login.html webpage
        # Assigns received user input values from HTTP POST Request to local variables with matching identifiers
        email = request.form.get("email").strip()
        password = request.form.get("password")

        customerData = getCustomerByEmail(email)
        barberData = getBarberByEmail(email)

        if customerData:
            if customerData["HashedPassword"] == hashPassword(password):
                flash("You have successfully logged in and been taken to the customer dashboard", category="Success")
                # Creates Customer object for Flask-Login
                customer = Customer(
                    customerId = customerData['CustomerID'],
                    firstName = customerData['FirstName'],
                    middleName = customerData['MiddleName'],
                    lastName = customerData['LastName'],
                    email = customerData['EmailAddress'],
                    hashedPassword = customerData['HashedPassword'],
                    isBlacklisted = customerData['IsBlackListed'],
                    phoneNumber = customerData['PhoneNumber']
                )
                login_user(customer, remember = True)
                return redirect("/customer_dashboard")
            else:
                flash("Incorrect Password. Please try again.", category = "Error")
        elif barberData:
            if barberData["HashedPassword"] == hashPassword(password):
                flash("You have successfully logged in and been taken to the barber dashboard", category="Success")
                barber = Barber(
                    barberId = barberData['BarberID'],
                    firstName = barberData['FirstName'],
                    middleName = barberData['MiddleName'],
                    lastName = barberData['LastName'],
                    email = barberData['EmailAddress'],
                    hashedPassword = barberData['HashedPassword'],
                    isAdmin = barberData['IsAdmin']
                )
                login_user(barber, remember = True)
                return redirect("/") # Link to barber dashboard
            else:
                flash("Incorrect Password. Please try again.", category = "Error")
        else:
            flash("Incorrect Email Address. Please try again, or create an account with that email.", category="Error")

    return render_template("webpages/user_management/login.html")

@userRedirection.route("/register", methods = ["GET", "POST"])
def register():
    error = False
    cleanupExpiredUnverified()

    firstName = ""
    middleName = ""
    lastName = ""
    email = ""
    phoneNumber = ""
    password1 = ""
    password2 = ""

    if request.method == "POST": # Evaluates the below block if receiving a POST request from the register.html webpage
        # Assigns received user input values from HTTP POST Request to local variables with matching identifiers
        firstName = request.form.get("firstName").strip()
        middleName = request.form.get("middleName").strip()
        lastName = request.form.get("lastName").strip()
        email = request.form.get("email").strip()
        phoneNumber = request.form.get("phoneNumber").strip()
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        # Ensures that no account already exists with the same email address
        customer = getCustomerByEmail(email)
        customerWithPhone = getCustomerByPhone(phoneNumber)
        print(customerWithPhone)
        if customer:
            flash("An account has already been created with this email address. Please login, or try again.", category="Error")
            error=True

        # Ensures that no account already exists with the same phone number, but allows empty fields
        elif customerWithPhone and phoneNumber != "":
            flash("An account has already been created with this phone number. Please try again with a different number." ,category="Error")
            error=True
        else:
            # Passes form inputs into registration validation procedures
            # The procedures return True if passes validation and False if it fails
            firstNameIsValidated = validateName(firstName, "First")
            middleNameIsValidated = validateName(middleName, "Middle")
            lastNameIsValidated = validateName(lastName, "Last")
            emailIsValidated = validateEmail(email)
            phoneNumberIsValidated = validatePhoneNumber(phoneNumber)
            passwordIsValidated = validatePassword(password1, password2)

            # If all validation check procedures are true, stores inputs in tblUnverified in database
            if firstNameIsValidated and middleNameIsValidated and lastNameIsValidated and emailIsValidated and phoneNumberIsValidated and passwordIsValidated:
                # Hashes password before storing
                hashedPassword = hashPassword(password1)

                # Creates unverified record in database
                verificationCode = generateOtp()

                unverifiedId = createUnverified(
                    firstName, middleName, lastName, email,
                    hashedPassword, phoneNumber, verificationCode, 0
                )

                # Stores only the unverified ID in cookie so that database records from that ID can be retrieved
                session["unverifiedID"] = unverifiedId

                return redirect("/verify_email")
            else:
                error=True
    if error:
        return render_template("webpages/user_management/register.html", firstName=firstName, middleName=middleName, lastName=lastName, email=email, phoneNumber=phoneNumber, password1=password1, password2=password2)
    else:
        return render_template("webpages/user_management/register.html")


@userRedirection.route("/logout")
@login_required # Only allows user to access this route if they are logged in
def logout():
    logout_user()
    flash("You have logged out and been returned to the home page.", category = "Success")
    return redirect("/")


@userRedirection.route("/verify_email", methods = ["GET", "POST"])
def verifyEmail():
    # Checks if there is a pending registration
    if "unverifiedID" not in session:
        flash("There is no pending registration. Please register or login.", category = "Error")
        return redirect("/register")

    # Retrieves unverified user ID record from database
    unverifiedId = session["unverifiedID"]
    unverifiedRecord = getUnverifiedById(unverifiedId, isPasswordReset = 0)

    if not unverifiedRecord:
        flash("Registration session expired. Please try again.", category = "Error")
        session.pop("unverifiedID", None)
        return redirect("/register")

    email = unverifiedRecord["EmailAddress"]
    verificationCode = unverifiedRecord["VerificationCode"]

    if request.method == "POST":
        getVerificationCode = request.form.get("otpCode").strip()

        if getVerificationCode == verificationCode:
            createCustomer(
                unverifiedRecord["FirstName"],
                unverifiedRecord["MiddleName"],
                unverifiedRecord["LastName"],
                unverifiedRecord["EmailAddress"],
                unverifiedRecord["HashedPassword"],
                unverifiedRecord["PhoneNumber"]
            )

            # Deletes unverified record
            deleteUnverified(unverifiedId)

            # Clears temporary cookie data once records are moved to tblCustomer
            session.pop("unverifiedID", None)

            flash("Your email has been verified.", category = "Success")
            flash("Account Successfully Created.", category = "Success")
            return redirect("/login")
        else:
            flash("Incorrect Verification Code. Please try again or return to 'Create Account'.", category="Error")

    elif request.method == "GET":
        # Sends verification email on first visit
        try:
            emailSent = sendVerificationEmail(email, verificationCode)
            if not emailSent:
                flash("Something went wrong in sending a verification email. Please try again.", category="Error")
                deleteUnverified(unverifiedId)
                session.pop("unverifiedID", None)
                return redirect("/register")
            else:
                flash("A verification code has been sent to your email inbox (if it exists). Please also check your junk folder.", category="Success")
        except:
            flash("An internet connection is required to create an account", category = "Error")
            return redirect("/register")
    return render_template("webpages/user_management/verify.html", is_password_reset = False)


@userRedirection.route("/forgot-password", methods = ["POST"])
def forgotPassword():
    # Handles password reset request from login page
    email = request.form.get("forgot_email").strip()

    # Checks if email exists in either customer or barber table
    customerData = getCustomerByEmail(email)
    barberData = getBarberByEmail(email)

    if customerData or barberData:
        otpCode = generateOtp()

        # Creates unverified record for password reset
        # Uses existing data from customer/barber table
        if customerData:
            unverifiedId = createUnverified(
                customerData['FirstName'],
                customerData['MiddleName'],
                customerData['LastName'],
                customerData['EmailAddress'],
                customerData['HashedPassword'],
                customerData['PhoneNumber'],
                otpCode,
                1  # Signals that isPasswordReset = True
            )
        else:
            # If the user is a barber
            unverifiedId = createUnverified(
                barberData['FirstName'],
                barberData['MiddleName'],
                barberData['LastName'],
                barberData['EmailAddress'],
                barberData['HashedPassword'],
                "",
                otpCode,
                1
            )

        # Stores only unverified ID in session
        session["unverifiedID"] = unverifiedId

        success = sendVerificationEmail(email, otpCode)

        if success:
            flash("Password reset code sent to your email!", category = "Success")
            return redirect("/verify_password_reset")
        else:
            flash("Failed to send email. Please try again.", category = "Error")
            deleteUnverified(unverifiedId)
            return redirect("/login")
    else:
        flash("No account exists with that email. Enter a different email or Create an Account.", category="Error")
        return redirect("/login")


@userRedirection.route("/verify_password_reset", methods = ["GET", "POST"])
def verifyPasswordReset():
    # Checks if the user has a pending password reset
    if "unverifiedID" not in session:
        flash("Please request a password reset first.", category = "Error")
        return redirect("/login")

    # Retrieves unverified record from database
    unverifiedId = session["unverifiedID"]
    unverifiedRecord = getUnverifiedById(unverifiedId, isPasswordReset = 1)

    if not unverifiedRecord:
        flash("Password reset session expired or invalid. Please try again.", category = "Error")
        session.pop("unverifiedID", None)
        return redirect("/login")

    if request.method == "POST":
        getOtp = request.form.get("otpCode").strip()
        storedOtp = unverifiedRecord["VerificationCode"]

        if getOtp == storedOtp:
            flash("Email verified. Please set your new password.", category="Success")
            return redirect("/set_new_password")
        else:
            flash("Incorrect verification code. Please try again.", category="Error")

    return render_template("webpages/user_management/verify.html", is_password_reset=True)


@userRedirection.route("/set_new_password", methods = ["GET", "POST"])
def setNewPassword():
    # Checks if user has completed OTP verification
    if "unverifiedID" not in session:
        flash("Please complete the password reset process from the beginning.", category="Error")
        return redirect("/login")

    # Retrieves unverified record
    unverifiedId = session["unverifiedID"]
    unverifiedRecord = getUnverifiedById(unverifiedId, isPasswordReset = 1)

    if not unverifiedRecord:
        flash("Password reset session expired or invalid. Please try again.", category="Error")
        session.pop("unverifiedID", None)
        return redirect("/login")

    if request.method == "POST":
        newPassword = request.form.get("new_password")
        confirmPassword = request.form.get("confirm_password")

        # Validates passwords using existing validation function
        if validatePassword(newPassword, confirmPassword):
            # Hashes the new password
            hashedPassword = hashPassword(newPassword)

            # Updates password in database
            email = unverifiedRecord["EmailAddress"]

            # Check which type of user and update accordingly
            customerData = getCustomerByEmail(email)
            barberData = getBarberByEmail(email)

            if customerData:
                updateCustomerPassword(email, hashedPassword)
            elif barberData:
                updateBarberPassword(email, hashedPassword)

            # Deletes unverified record
            deleteUnverified(unverifiedId)

            # Clears the cookie storing the unverifiedID from the session
            session.pop("unverifiedID", None)

            flash("Password reset successful! Please login with your new password.", category="Success")
            return redirect("/login")

    return render_template("webpages/user_management/forgot_password.html")