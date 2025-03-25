import os
import smtplib
from email.mime.text import MIMEText

smtp_user = os.environ["SMTP_USER"]
smtp_password = os.environ["SMTP_PASSWORD"]
smtp_server = os.environ["SMTP_SERVER"]
smtp_port = int(os.environ["SMTP_PORT"])
sender_email = os.environ["SENDER_EMAIL"]
to_email = os.environ["TO_EMAIL"]

# Compose a simple test email
subject = "Test Email from Python"
body = "Hello from your fren’s automated Python emailer!"

msg = MIMEText(body)
msg["Subject"] = subject
msg["From"] = sender_email
msg["To"] = to_email

# Send the email
try:
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        print("✅ Email sent successfully!")
except Exception as e:
    print(f"❌ Error sending email: {e}")
