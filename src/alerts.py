
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ========== CONFIG ==========
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("SMTP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
# ============================

def send_email_alert(ip, level):
    if not all([SENDER_EMAIL, APP_PASSWORD, RECEIVER_EMAIL]):
        print("[EMAIL ERROR] Email configuration is missing.")
        return

    try:
        subject = f"🚨 DecoyShield Alert - {level} Threat"

        body = f"""
        High Threat Detected!

        Attacker IP: {ip}
        Threat Level: {level}

        Please check DecoyShield Dashboard immediately.
        """

        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)

        print("[EMAIL ALERT SENT]")

    except Exception as e:
        print("[EMAIL ERROR]", e)
