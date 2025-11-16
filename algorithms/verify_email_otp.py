import random
# Allows random number generation functions

from flask import flash
# Allows messages to be flashed to the user

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# Allows emails to be sent with the SMTP protocol

# Generates a random 6 digit number
def generate_otp() -> str:
    otpCode = ""
    for digit in range(0, 6):
        otpCode = otpCode + str(random.randint(0, 9))
    return otpCode


def send_verification_email(senderEmail: str, receiverEmail: str, emailPassword: str, otpCode: str) -> None:
    # Sends a verification email containing the OTP code using Gmail's SMTP server
    # Email Content
    subject = "Your Email Verification Code"
    body = "Your verification code is: " + otpCode

    message = MIMEMultipart()
    message["From"] = senderEmail
    message["To"] = receiverEmail
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # Use STARTTLS on port 587
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            # Identify ourselves to the server
            server.ehlo()
            # Upgrades the connection to a secure encrypted TLS connection
            server.starttls()
            server.ehlo()

            # Log in to the email account using the app password
            server.login(senderEmail, emailPassword)

            # Send the message
            server.send_message(message)
            flash("A verification email has been sent to your inbox. Enter the received code below.", category = "Success")
    except smtplib.SMTPException:
        # Handles errors without crashing the program if there is an issue
        flash("Something went wrong in sending a verification email. Please try again.", category = "Error")

if __name__ == "__main__":
    # Generates a random 6 digit code to send to the user as a verification email
    verificationCode = generate_otp()

    # Email Configuration
    sendingEmail = "157adampatel@gmail.com"
    receivingEmail = "adampatel157@outlook.com"
    password = "cmfv nffy fscy usmu" # Google App Password created for email account

    send_verification_email(sendingEmail, receivingEmail, password, verificationCode)