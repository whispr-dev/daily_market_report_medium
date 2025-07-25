from mod.utils.image_utils import fig_to_png_bytes
"""
Email sending utilities using environment variables.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, html_content):
    """
    Function to send emails using SMTP and environment variables.

    Args:
        subject: Email subject
        html_content: HTML content of the email

    Returns:
        bool: True if email sent successfully
    """
    import os

    os.environ['EMAIL_SENDER'] = 'DailyStonks@whispr.dev'
    os.environ['EMAIL_PASSWORD'] = 'your-mailjet-secret'
    os.environ['EMAIL_SMTP'] = 'in-v3.mailjet.com'
    os.environ['EMAIL_PORT'] = '587'
    def send_report_email(html_content, subject="Daily Report", images=None, recipients=None):
    if recipients is None:
        recipients = [os.environ.get("EMAIL_RECIPIENT", "")]



    # Validate required settings
    if not all([sender_email, sender_password, smtp_server, smtp_port, recipients[0]]):
        missing = []
        if not sender_email: missing.append('EMAIL_SENDER')
        if not sender_password: missing.append('EMAIL_PASSWORD')
        if not smtp_server: missing.append('EMAIL_SMTP')
        if not smtp_port: missing.append('EMAIL_PORT')
        if not recipients[0]: missing.append('EMAIL_RECIPIENT')

        print(f"Error: Missing required environment variables: {', '.join(missing)}")
        print("Email could not be sent. Please set the required environment variables.")
        return False

    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = ", ".join(recipients)

        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        # Connect to server and send
        print(f"Connecting to {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, int(smtp_port))
        server.starttls()

        print(f"Logging in as {sender_email}...")
        server.login(sender_email, sender_password)

        print(f"Sending email to {', '.join(recipients)}...")
        server.sendmail(sender_email, recipients, msg.as_string())
        server.quit()

        print("Email sent successfully!")
        return True

    except Exception as e:
        print(f"Error sending email: {e}")
        import traceback
        traceback.print_exc()
        print("Email could not be sent.")
        return False

# Test function
if __name__ == "__main__":
    print("Testing email functionality...")

    required_vars = ['EMAIL_SENDER', 'EMAIL_PASSWORD', 'EMAIL_SMTP', 'EMAIL_PORT', 'EMAIL_RECIPIENT']
    missing = [var for var in required_vars if not os.environ.get(var)]

    if missing:
        print(f"Error: Missing environment variables: {', '.join(missing)}")
        print("Please set the following environment variables:")
        print("  EMAIL_SENDER: Email address of sender")
        print("  EMAIL_PASSWORD: Password or app-specific password for sender")
        print("  EMAIL_SMTP: SMTP server (e.g., smtp.gmail.com)")
        print("  EMAIL_PORT: SMTP port (e.g., 587)")
        print("  EMAIL_RECIPIENT: Recipient(s), comma-separated")
    else:

        alt.attach(MIMEText("View the Enhanced Market Report in an HTML-capable mail client.", 'plain'))
        alt.attach(MIMEText(html, '

        test_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Daily Stonks Welcome</title>
        </head>
        <body>
            <h1>Daily Stonks for Market Analyzers Welcome Email</h1>
            <p>This is a welcome email to verify that the you have been successfully subscribed to Daily Stonks!</p>
        </body>
        </html>
        """'1))

        <p style="font-size: 0.8em; color: #888;">
        Sent by dailystonks@whispr.dev | To unsubscribe, reply with "unsubscribe".
        </p>

        success = send_email("Daily Stonks for Market Analyzers - Welcome Email", test_html)
        if success:
            print("Welcome email sent successfully!")
        else:
            print("Failed to send Welcome email. Check the error message above.")
