from flask import Blueprint, render_template, request, flash, redirect, session
# 'Blueprint' library allows different sections of a Flask application to be organised into separate modules.
# 'render_template' library allows HTML templates to be displayed dynamically through Python code.
# 'request' library allows data to be accessed from incoming HTTP requests, such as form submissions.
# 'flash' library allows for the system to display temporary feedback messages to the user's screen.
# 'redirect' library allows the system to automatically navigate the user to a different webpage or route.
# 'session' library allows data to be stored temporarily in cookies.

from .models import tblCustomer, tblBarber, tblUnverified
# Allows the system to add new records to tblCustomer by accessing its class in models.py

from . import db

from algorithms.hash_password import hash_password

from algorithms.email_otp import generate_otp, send_verification_email

# Imports the SHA-256 hashing algorithm for passwords from the hash_password file

from flask_login import login_user, logout_user, login_required

from algorithms.time_limits import cleanup_expired_unverified

user_redirection = Blueprint("auth", __name__)

# Registration Validation Functions
# If validation test for field passes, returns True
# If validation test for field fails, returns False and displays error message
# All functions must return True for registration to be successful

def validateName(name, namePos):
    lowercaseEnglishAlphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    if (len(name) < 2) and (namePos != "Middle"): # Allows empty middle name fields
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
    if phoneNum == "": # Allows empty phone number fields as it is optional
        return True
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
                login_user(customer, remember=True)
                return redirect("/customer_dashboard")
            else:
                flash("Incorrect Password. Please try again.", category="Error")
        elif barber:
            if barber.HashedPassword == hash_password(password):
                flash("You have successfully logged in and been taken to the barber dashboard", category="Success")
                login_user(barber, remember=True)
                return redirect("/") # Link to barber dashboard
            else:
                flash("Incorrect Password. Please try again.", category="Error")
        else:
            flash("Incorrect Email Address. Please try again, or create an account with that email.", category="Error")

    return render_template("webpages/user_management/login.html")

@user_redirection.route("/register", methods=["GET", "POST"])
def register():
    # Cleans up expired unverified records
    cleanup_expired_unverified(db, tblUnverified)

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
        customer = tblCustomer.query.filter_by(EmailAddress = email).first()
        if customer:
            flash("An account has already been created with this email address. Please login, or try again.", category="Error")
            return redirect("/register")

        # Ensures that no account already exists with the same phone number, but allows empty fields
        customerWithPhone = tblCustomer.query.filter_by(PhoneNumber = phoneNumber).first()
        if customerWithPhone and customerWithPhone != "":
            flash("An account has already been created with this phone number. Please try again with a different number." ,category="Error")
            return redirect("/register")

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
            hashedPassword = hash_password(password1)

            # Creates unverified record in database
            verificationCode = generate_otp()

            # noinspection PyArgumentList
            newUnverified = tblUnverified(
                FirstName=firstName,
                MiddleName=middleName,
                LastName=lastName,
                EmailAddress=email,
                HashedPassword=hashedPassword,
                PhoneNumber=phoneNumber,
                VerificationCode=verificationCode,
                IsPasswordReset=False
            )
            db.session.add(newUnverified)
            db.session.commit()

            # Stores only the unverified ID in cookie so that database records from that ID can be retrieved
            session["unverifiedID"] = newUnverified.UnverifiedID

            return redirect("/verify_email")

    return render_template("webpages/user_management/register.html")

@user_redirection.route("/logout")
@login_required # Only allows user to access this route if they are logged in
def logout():
    logout_user()
    flash("You have logged out and been returned to the home page.", category="Success")
    return redirect("/")


@user_redirection.route("/verify_email", methods=["GET", "POST"])
def verify_email():
    # Checks if there is a pending registration
    if "unverifiedID" not in session:
        flash("There is no pending registration. Please register or login.", category="Error")
        return redirect("/register")

    # Retrieves unverified user ID record from database
    unverifiedID = session["unverifiedID"]
    unverifiedRecord = tblUnverified.query.filter_by(UnverifiedID=unverifiedID, IsPasswordReset=False).first()

    if not unverifiedRecord:
        flash("Registration session expired. Please try again.", category="Error")
        session.pop("unverifiedID", None)
        return redirect("/register")

    email = unverifiedRecord.EmailAddress
    verificationCode = unverifiedRecord.VerificationCode

    # Email Configuration
    sendingEmail = "157adampatel@gmail.com"
    receivingEmail = email
    password = "cmfv nffy fscy usmu"

    if request.method == "POST":
        getVerificationCode = request.form.get("otpCode").strip()

        if getVerificationCode == verificationCode:
            # noinspection PyArgumentList
            newCustomer = tblCustomer(
                FirstName=unverifiedRecord.FirstName,
                MiddleName=unverifiedRecord.MiddleName,
                LastName=unverifiedRecord.LastName,
                EmailAddress=unverifiedRecord.EmailAddress,
                HashedPassword=unverifiedRecord.HashedPassword,
                IsBlackListed=False,
                PhoneNumber=unverifiedRecord.PhoneNumber
            )
            db.session.add(newCustomer)

            # Deletes unverified record
            db.session.delete(unverifiedRecord)
            db.session.commit()

            # Clears temporary cookie data once records are moved to tblCustomer
            session.pop("unverifiedID", None)

            flash("Your email has been verified.", category="Success")
            flash("Account Successfully Created.", category="Success")
            return redirect("/login")
        else:
            flash("Incorrect Verification Code. Please try again or return to 'Create Account'.", category="Error")

    elif request.method == "GET":
        # Send verification email on first visit
        try:
            emailSent = send_verification_email(sendingEmail, receivingEmail, password, verificationCode)
            if not emailSent:
                flash("Something went wrong in sending a verification email. Please try again.", category="Error")
                db.session.delete(unverifiedRecord)
                db.session.commit()
                session.pop("unverifiedID", None)
                return redirect("/register")
            else:
                flash("A verification code has been sent to your email inbox (if it exists). Please also check your junk folder.", category="Success")
        except:
            flash("An internet connection is required to create an account", category="Error")
            return redirect("/register")
    return render_template("webpages/user_management/verify.html", is_password_reset=False)


@user_redirection.route("/forgot-password", methods=["POST"])
def forgot_password():
    # Handles password reset request from login page
    email = request.form.get("forgot_email").strip()

    # Check if email exists in either customer or barber table
    customer = tblCustomer.query.filter_by(EmailAddress = email).first()
    barber = tblBarber.query.filter_by(EmailAddress = email).first()

    if customer or barber:
        # Generate OTP code
        otpCode = generate_otp()

        # Create unverified record for password reset
        # Use existing data from customer/barber table
        if customer:
            # noinspection PyArgumentList
            resetRecord = tblUnverified(
                FirstName = customer.FirstName,
                MiddleName = customer.MiddleName,
                LastName = customer.LastName,
                EmailAddress = customer.EmailAddress,
                HashedPassword = customer.HashedPassword,
                PhoneNumber = customer.PhoneNumber,
                VerificationCode = otpCode,
                IsPasswordReset = True
            )
        else:
            # If the user is a barber
            # noinspection PyArgumentList
            resetRecord = tblUnverified(
                FirstName=barber.FirstName,
                MiddleName=barber.MiddleName,
                LastName=barber.LastName,
                EmailAddress=barber.EmailAddress,
                HashedPassword=barber.HashedPassword,
                PhoneNumber="",
                VerificationCode=otpCode,
                IsPasswordReset=True
            )

        db.session.add(resetRecord)
        db.session.commit()

        # Stores only unverified ID in session
        session["unverifiedID"] = resetRecord.UnverifiedID

        # Sends verification email
        senderEmail = "157adampatel@gmail.com"
        emailPassword = "cmfv nffy fscy usmu"

        success = send_verification_email(
            senderEmail,
            email,
            emailPassword,
            otpCode
        )

        if success:
            flash("Password reset code sent to your email!", category="Success")
            return redirect("/verify_password_reset")
        else:
            flash("Failed to send email. Please try again.", category="Error")
            db.session.delete(resetRecord)
            db.session.commit()
            return redirect("/login")
    else:
        flash("No account exists with that email. Enter a different email or Create an Account.", category="Error")
        return redirect("/login")


@user_redirection.route("/verify_password_reset", methods=["GET", "POST"])
def verify_password_reset():
    # Checks if the user has a pending password reset
    if "unverifiedID" not in session:
        flash("Please request a password reset first.", category="Error")
        return redirect("/login")

    # Retrieves unverified record from database
    unverifiedID = session["unverifiedID"]
    unverifiedRecord = tblUnverified.query.filter_by(UnverifiedID=unverifiedID, IsPasswordReset=True).first()

    if not unverifiedRecord:
        flash("Password reset session expired or invalid. Please try again.", category="Error")
        session.pop("unverifiedID", None)
        return redirect("/login")

    if request.method == "POST":
        getOtp = request.form.get("otpCode").strip()
        storedOtp = unverifiedRecord.VerificationCode

        if getOtp == storedOtp:
            flash("Email verified. Please set your new password.", category="Success")
            return redirect("/set_new_password")
        else:
            flash("Incorrect verification code. Please try again.", category="Error")

    return render_template("webpages/user_management/verify.html", is_password_reset=True)


@user_redirection.route("/set_new_password", methods=["GET", "POST"])
def set_new_password():
    # Checks if user has completed OTP verification
    if "unverifiedID" not in session:
        flash("Please complete the password reset process from the beginning.", category="Error")
        return redirect("/login")

    # Retrieves unverified record
    unverifiedID = session["unverifiedID"]
    unverifiedRecord = tblUnverified.query.filter_by(UnverifiedID=unverifiedID, IsPasswordReset=True).first()

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
            hashedPassword = hash_password(newPassword)

            # Updates password in database
            email = unverifiedRecord.EmailAddress
            customer = tblCustomer.query.filter_by(EmailAddress=email).first()
            barber = tblBarber.query.filter_by(EmailAddress=email).first()

            if customer:
                customer.HashedPassword = hashedPassword
            elif barber:
                barber.HashedPassword = hashedPassword

            # Deletes unverified record
            db.session.delete(unverifiedRecord)
            db.session.commit()

            # Clears the cookie storing the unverifiedID from the session
            session.pop("unverifiedID", None)

            flash("Password reset successful! Please login with your new password.", category="Success")
            return redirect("/login")

    return render_template("webpages/user_management/forgot_password.html")