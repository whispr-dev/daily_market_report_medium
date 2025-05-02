"""
Email sending functionality for market reports using environment variables.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import traceback

def send_report_email(html_content, subject="Daily Stock Market Report"):
    """
    Send HTML report via email, using settings from environment variables.
    
    Required environment variables:
        EMAILSENDER: Email address of sender
        EMAILPASSWORD: Password or app-specific password for sender
        EMAILSMTP: SMTP server (e.g., smtp.gmail.com)
        EMAILPORT: SMTP port (e.g., 587)
        EMAILRECIPIENT: Email address(es) of recipient(s), comma-separated
        
    Args:
        html_content: HTML content of the report
        subject: Email subject
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Get email settings from environment variables
        sender_email = os.environ.get('EMAILSENDER')
        sender_password = os.environ.get('EMAILPASSWORD')
        smtp_server = os.environ.get('EMAILSMTP')
        smtp_port = os.environ.get('EMAILPORT')
        recipients = os.environ.get('EMAILRECIPIENT', '').split(',')
        
        # Validate required settings
        if not all([sender_email, sender_password, smtp_server, smtp_port, recipients[0]]):
            missing = []
            if not sender_email: missing.append('EMAILSENDER')
            if not sender_password: missing.append('EMAILPASSWORD')
            if not smtp_server: missing.append('EMAILSMTP')
            if not smtp_port: missing.append('EMAILPORT')
            if not recipients[0]: missing.append('EMAILRECIPIENT')
            
            print(f"Error: Missing required environment variables: {', '.join(missing)}")
            print("Email could not be sent. Please set the required environment variables.")
            return False
        
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
        server.starttls()  # Secure the connection
        
        print(f"Logging in as {sender_email}...")
        server.login(sender_email, sender_password)
        
        print(f"Sending email to {', '.join(recipients)}...")
        server.sendmail(sender_email, recipients, msg.as_string())
        server.quit()
        
        print("Email sent successfully!")
        return True
    
    except Exception as e:
        print(f"Error sending email: {e}")
        traceback.print_exc()
        print("Email could not be sent, but HTML report was saved locally.")
        return False

if __name__ == "__main__":
    # Test email functionality
    print("Testing email functionality...")
    
    # Check if environment variables are set
    required_vars = ['EMAILSENDER', 'EMAILPASSWORD', 'EMAILSMTP', 'EMAILPORT', 'EMAILRECIPIENT']
    missing = [var for var in required_vars if not os.environ.get(var)]
    
    if missing:
        print(f"Error: Missing environment variables: {', '.join(missing)}")
        print("Please set the following environment variables:")
        print("  EMAILSENDER: Email address of sender")
        print("  EMAILPASSWORD: Password or app-specific password for sender")
        print("  EMAILSMTP: SMTP server (e.g., smtp.gmail.com)")
        print("  EMAILPORT: SMTP port (e.g., 587)")
        print("  EMAILRECIPIENT: Email address(es) of recipient(s), comma-separated")
    else:
        # Send test email
        test_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Test Email</title>
        </head>
        <body>
            <h1>Stock Market Analyzer Test Email</h1>
            <p>This is a test email to verify that the email functionality is working correctly.</p>
            <p>If you're receiving this email, the configuration is correct!</p>
        </body>
        </html>
        """
        
        success = send_report_email(test_html, "Stock Market Analyzer - Test Email")
        
        if success:
            print("Test email sent successfully!")
        else:
            print("Failed to send test email. Check the error message above.")