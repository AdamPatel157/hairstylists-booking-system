from flask import Blueprint, render_template, request, flash, redirect
# 'Blueprint' library allows...
# 'render_template' library allows...
# 'request' library allows...
# 'flash' library allows for the system to display temporary messages to the user's screen

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
    data = request.form # Accesses the form attribute data from the incoming POST Request
    print(data)
    return render_template("webpages/user_management/login.html")

@user_redirection.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST": # Evaluates the below block if receiving data from the register webpage
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
            flash("Account Successfully Created.", category = "Success")
            return redirect("/login")

    return render_template("webpages/user_management/register.html")

@user_redirection.route("/logout")
def logout():
    flash("You have logged out and been returned to the home page.", category="Success")
    return redirect("/")