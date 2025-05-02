"""
Simple email sending module for the stock market analyzer.
"""

def send_email(subject, html_content, recipients=None, sender=None):
    """
    Mock function to simulate sending email.
    
    Args:
        subject: Email subject
        html_content: HTML content of the email
        recipients: List of recipient email addresses (optional)
        sender: Sender email address (optional)
    
    Returns:
        bool: Success indicator
    """
    print("\n" + "="*70)
    print(" EMAIL WOULD BE SENT")
    print("="*70)
    print(f" Subject: {subject}")
    print(f" Content length: {len(html_content)} characters")
    if recipients:
        print(f" Recipients: {recipients}")
    if sender:
        print(f" Sender: {sender}")
    print("-"*70)
    print(" (No actual emails are sent - this is a mock function)")
    print(" To implement real email sending, configure SMTP settings in this module")
    print("="*70 + "\n")
    
    return True

# You can implement real email sending by uncommenting and configuring the code below:
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-email@gmail.com"  # Change this
SMTP_PASSWORD = "your-app-password"     # Change this (use App Password for Gmail)

# Default sender and recipients
DEFAULT_SENDER = "your-email@gmail.com"  # Change this
DEFAULT_RECIPIENTS = ["recipient@example.com"]  # Change this

def send_email(subject, html_content, recipients=None, sender=None):
    '''
    Send an HTML email.
    
    Args:
        subject: Email subject
        html_content: HTML content of the email
        recipients: List of recipient email addresses (optional)
        sender: Sender email address (optional)
    
    Returns:
        bool: Success indicator
    '''
    try:
        # Use default values if not provided
        if not recipients:
            recipients = DEFAULT_RECIPIENTS
        if not sender:
            sender = DEFAULT_SENDER
            
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))
        
        # Connect to SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        print(f"Email sent successfully to {recipients}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
"""