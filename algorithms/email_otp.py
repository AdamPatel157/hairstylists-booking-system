import random
# Allows random number generation functions

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

def send_verification_email(receiverEmail: str, otpCode: str):
    # Sends a verification email containing the OTP code using Gmail's SMTP server
    # Email Content
    subject = "Your Email Verification Code"
    body = "Your verification code is: " + otpCode

    senderEmail = "ganihairbookings@gmail.com"
    emailPassword = "ykyj bzqn jgos jhmd" # Google App Password created for email account

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
            print("Verification email sent successfully")
            return True

    except smtplib.SMTPException:
        # Handles errors without crashing the program if there is an issue
        print("Email failed to send.")
        return False

# For testing the individual module:

if __name__ == "__main__":
    verificationCode = generate_otp()
    receivingEmail = input("Enter your email address: ")
    send_verification_email(receivingEmail, verificationCode)