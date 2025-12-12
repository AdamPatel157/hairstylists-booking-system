import random
# Allows random number generation functions

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from website.database_management import getBookingDetails
from website.user_friendly_names import userFriendlyServiceNames

# Allows emails to be sent with the SMTP protocol

# Generates a random 6 digit number
def generateOtp():
    otpCode = ""
    for digit in range(0, 6):
        otpCode = otpCode + str(random.randint(0, 9))
    return otpCode

def sendVerificationEmail(receiverEmail: str, otpCode: str):
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


def sendBookingConfirmationEmail(bookingReference: int):
    details = getBookingDetails(bookingReference)
    if not details:
        print("No booking found for reference:", bookingReference)
        return False

    receiverEmail = details["customerEmail"]

    friendlyServices = [userFriendlyServiceNames(service) for service in details["services"]]
    servicesList = ", ".join(friendlyServices)

    subject = f"Booking Confirmation - Reference: #{bookingReference}"

    body = (
        f"Dear {details['customerName']},\n\n"
        f"Your booking has been confirmed!\n\n"
        f"Booking Reference: {details['bookingReference']}\n\n"
        f"Shop Address:\n72 Hartington Rd,\nLeicester,\nLE2 0GN\n\n"
        f"Appointment Date: {details['selectedDate']} ({details['selectedDay']})\n"
        f"Time: {details['startTime']} - {details['endTime']}\n\n"
        f"Total Price: £{(details['totalPrice'] + 5):.2f}\n"
        f"Barber: {details['barberName']}\n"
        f"Services: {servicesList}\n\n"
        f"Additional Notes for Barber: {details['noteForBarber'] if details['noteForBarber'] else 'None'}\n\n"
        f"Reminder: We only accept cash payments in-store.\n\n"
        f"If you need to cancel or have any issues, please contact 07773 326497 by phone or SMS.\n"
    )

    senderEmail = "ganihairbookings@gmail.com"
    emailPassword = "ykyj bzqn jgos jhmd"  # Google App Password created for email account

    message = MIMEMultipart()
    message["From"] = senderEmail
    message["To"] = receiverEmail
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()

            server.login(senderEmail, emailPassword)
            server.send_message(message)

            print("Booking confirmation email sent successfully")
            return True

    except smtplib.SMTPException as error:
        print("Booking confirmation email failed to send:", error)
        return False


# For testing the individual module:

if __name__ == "__main__":
    verificationCode = generateOtp()
    receivingEmail = input("Enter your email address: ")
    sendVerificationEmail(receivingEmail, verificationCode)