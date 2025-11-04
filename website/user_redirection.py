from flask import Blueprint, render_template, request, flash
# 'Blueprint' library allows...
# 'render_template' library allows...
# 'request' library allows...
# 'flash' library allows for the system to display temporary messages to the user's screen

user_redirection = Blueprint("auth", __name__)

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

        # Registration Form Input Validation:

        # Name Fields Validation:

        lowercaseEnglishAlphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
                                    'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

        passwordPunctuation = ['?', '!', '£', '%', '^', '&', '*', '(', ')', '/', '#']

        numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

        if len(firstName) < 2:
            flash("First Name must be greater than 1 character long.", category="Error")
        elif any(character.lower() not in lowercaseEnglishAlphabet for character in firstName):
            flash("First Name can only contain English alphabet characters.", category="Error")

        elif len(lastName) < 2: # Ensures the length of last names are not 0 or 1 character long
            flash("Last Name must be greater than 1 character long.", category="Error")
        elif any(character.lower() not in lowercaseEnglishAlphabet for character in firstName):
            flash("Last Name can only contain English alphabet characters.", category="Error")
            # Ensures last names only contain English alphabet characters

        # No Length Validation for middleName as middleName is an optional field so can have 0 characters if left blank
        elif len(middleName) > 0:
            for character in middleName:
                if character.lower() not in lowercaseEnglishAlphabet: # Ensures middle names only contain English alphabet characters
                    flash("Middle Name can only contain English alphabet characters.", category="Error")

        # Email Validation:

        elif len(email) < 4:
            flash("Length of Email must be greater than 3 characters long.", category="Error")

        elif "@" not in email or "." not in email:
            flash("Email must contain '@' and '.' symbols.", category="Error")

        # Phone Number Validation:

        elif len(phoneNumber) > 0:
            if len(phoneNumber) != 11:
                flash("Phone Numbers must be exactly 11 characters long.", category="Error")
            else:
                for character in phoneNumber:
                    if character not in numbers:
                        flash("Phone Numbers can only contain integer numbers 0-9.", category="Error")
                if phoneNumber[0] != '0':
                    flash("Phone Numbers must begin with the number '0'.", category="Error")

        # Password Validation:

        elif len(password1) < 8:
            flash("Passwords must be at least 8 characters in length.", category="Error")

        elif not any(character.lower() in lowercaseEnglishAlphabet for character in password1):
            flash("Passwords must contain at least one English alphabet character.", category="Error")

        elif not any(character in numbers for character in password1):
            flash("Passwords must contain at least one integer number 0-9.", category="Error")

        elif not any(character in passwordPunctuation for character in password1):
            flash("Passwords must contain at least one punctuation character from "
                  "['?', '!', '£', '%', '^', '&', '*', '(', ')', '/', '#'].", category="Error")

        elif password1 == password1.lower(): # If there are no uppercase letters
            flash("Passwords must contain at least one uppercase letter.", category="Error")

        elif password1 == password1.upper(): # If there are no lowercase letters
            flash("Passwords must contain at least one lowercase letter.", category="Error")

        elif password1 != password2: # If the confirmation password does not equal the created password
            flash("Passwords do not match.", category="Error")

        else:
            flash("Account Successfully Created.", category = "Success")

    return render_template("webpages/user_management/register.html")

@user_redirection.route("/logout")
def logout():
    return "<p>You have successfully logged out</p>"