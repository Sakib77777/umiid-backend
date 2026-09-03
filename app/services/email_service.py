import smtplib
from email.mime.text import MIMEText

from app.config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD, OTP_EXPIRY_MINUTES

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def send_otp_email(to_email: str, otp: str) -> None:
    subject = "Your UMIID password reset code"
    body = (
        f"Your password reset code is: {otp}\n\n"
        f"This code expires in {OTP_EXPIRY_MINUTES} minute(s).\n"
        f"If you didn't request this, you can safely ignore this email."
    )

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = GMAIL_ADDRESS
    message["To"] = to_email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, to_email, message.as_string())