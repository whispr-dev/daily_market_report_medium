"""
Email sending functionality for market reports.
"""
import traceback

def send_report_email(html_content, subject="Daily Stonk Market Report"):
    """
    Send HTML report via email.
    
    Args:
        html_content: HTML content of the report
        subject: Email subject
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Import here to avoid circular imports
        from sendemail import send_email
        
        # Send the email
        send_email(subject, html_content)
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        traceback.print_exc()
        print("Email could not be sent, but HTML report was saved locally.")
        return False