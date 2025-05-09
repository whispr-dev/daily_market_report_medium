import os
import time
import queue
import hashlib
import hmac
import threading
import traceback
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from premailer import transform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/email_sender.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EmailQueue:
    """
    Queue system for rate-limiting email sending.
    """
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one queue exists."""
        if cls._instance is None:
            cls._instance = super(EmailQueue, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        """Initialize the email queue."""
        self.queue = queue.Queue()
        self.rate_limit = int(os.environ.get('EMAIL_RATE_LIMIT', 10))  # Emails per period
        self.period = int(os.environ.get('EMAIL_RATE_PERIOD', 3600))   # Period in seconds
        self.sent_count = 0
        self.reset_time = time.time() + self.period
        self.lock = threading.Lock()
        
        # Start worker thread
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        
        logger.info(f"Email queue initialized (Rate: {self.rate_limit}/{self.period}s)")
    
    def _worker(self):
        """Worker thread to process email queue."""
        while True:
            try:
                # Get next email job
                email_job = self.queue.get()
                
                # Check rate limit
                with self.lock:
                    current_time = time.time()
                    
                    # Reset counter if period has elapsed
                    if current_time > self.reset_time:
                        self.sent_count = 0
                        self.reset_time = current_time + self.period
                    
                    # Wait if rate limit reached
                    while self.sent_count >= self.rate_limit:
                        sleep_time = self.reset_time - current_time
                        if sleep_time > 0:
                            logger.info(f"Rate limit reached, waiting {sleep_time:.1f}s")
                            time.sleep(sleep_time)
                        
                        # Reset counter
                        current_time = time.time()
                        if current_time > self.reset_time:
                            self.sent_count = 0
                            self.reset_time = current_time + self.period
                
                # Process email
                recipient, subject, html_content, images, is_report = email_job
                success = self._send_email(recipient, subject, html_content, images, is_report)
                
                if success:
                    with self.lock:
                        self.sent_count += 1
                    
                    logger.info(f"Email sent to {recipient}")
                else:
                    logger.error(f"Failed to send email to {recipient}")
                
                # Mark task as done
                self.queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in email worker: {e}")
                time.sleep(1)  # Avoid tight loop in case of errors
    
    def _send_email(self, recipient, subject, html_content, images=None, is_report=False):
        """
        Actually send the email.
        
        Args:
            recipient (str): Email recipient
            subject (str): Email subject
            html_content (str): HTML email content
            images (dict): Optional images to include
            is_report (bool): Whether this is a report email
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            sender_email = os.environ.get('EMAIL_SENDER')
            sender_password = os.environ.get('EMAIL_PASSWORD')
            smtp_server = os.environ.get('EMAIL_SMTP')
            smtp_port = int(os.environ.get('EMAIL_PORT', 587))

            # Validate environment
            if not all([sender_email, sender_password, smtp_server, smtp_port, recipient]):
                logger.error("Missing required email configuration")
                return False

            # Generate unsubscribe token if this is a report
            if is_report:
                unsubscribe_token = generate_unsubscribe_token(recipient)
                unsubscribe_url = f"https://whispr.dev/unsubscribe?email={recipient}&token={unsubscribe_token}"
            else:
                unsubscribe_url = f"https://whispr.dev/unsubscribe?email={recipient}"

            # Inline CSS for email clients
            email_ready_html = transform(html_content)

            # Create message
            msg = MIMEMultipart('related')
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = recipient
            msg['List-Unsubscribe'] = f"<{unsubscribe_url}>"

            # Add alternative parts
            alt = MIMEMultipart('alternative')
            plain_text = "This email contains HTML content. Please use an HTML-capable email client to view it properly."
            alt.attach(MIMEText(plain_text, 'plain'))
            alt.attach(MIMEText(email_ready_html, 'html'))
            msg.attach(alt)

            # Add images if provided
            if images:
                for cid, img_bytes in images.items():
                    img = MIMEImage(img_bytes, 'png')
                    img.add_header('Content-ID', f'<{cid}>')
                    img.add_header('Content-Disposition', 'inline', filename=f'{cid}.png')
                    msg.attach(img)

            # Connect and send
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()

            return True

        except Exception as e:
            logger.error(f"Email send failed: {e}")
            traceback.print_exc()
            return False
    
    def add_to_queue(self, recipient, subject, html_content, images=None, is_report=False):
        """
        Add email to sending queue.
        
        Args:
            recipient (str): Email recipient
            subject (str): Email subject
            html_content (str): HTML email content
            images (dict): Optional images to include
            is_report (bool): Whether this is a report email
            
        Returns:
            bool: True if added to queue successfully
        """
        try:
            self.queue.put((recipient, subject, html_content, images, is_report))
            return True
        except Exception as e:
            logger.error(f"Error adding email to queue: {e}")
            return False
    
    def wait_completion(self, timeout=None):
        """
        Wait for all queued emails to be sent.
        
        Args:
            timeout (float): Maximum time to wait in seconds
            
        Returns:
            bool: True if all emails were sent, False if timeout occurred
        """
        try:
            self.queue.join(timeout=timeout)
            return True
        except queue.Empty:
            return False

def generate_unsubscribe_token(email):
    """
    Generate a secure unsubscribe token.
    
    Args:
        email: Subscriber's email
        
    Returns:
        str: Secure unsubscribe token
    """
    secret_key = os.environ.get('SECRET_KEY', 'dailystonks-secret-key')
    timestamp = int(time.time())
    payload = f"{email}:{timestamp}"
    token = hmac.new(secret_key.encode(), payload.encode(), 'sha256').hexdigest()
    return f"{token}:{timestamp}"

def validate_unsubscribe_token(email, token, max_age=604800):  # Default 7 days
    """
    Validate an unsubscribe token.
    
    Args:
        email (str): Subscriber email
        token (str): Token to validate
        max_age (int): Maximum token age in seconds
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    try:
        # Parse token
        token_parts = token.split(':')
        if len(token_parts) != 2:
            return False
        
        signature, timestamp_str = token_parts
        timestamp = int(timestamp_str)
        
        # Check if token is expired
        current_time = int(time.time())
        if current_time - timestamp > max_age:
            return False
        
        # Verify signature
        secret_key = os.environ.get('SECRET_KEY', 'dailystonks-secret-key')
        payload = f"{email}:{timestamp}"
        expected_signature = hmac.new(secret_key.encode(), payload.encode(), 'sha256').hexdigest()
        
        return signature == expected_signature
        
    except Exception as e:
        logger.error(f"Error validating unsubscribe token: {e}")
        return False

def add_watermark_to_chart(fig, email):
    """
    Add a subtle watermark to a matplotlib figure.
    
    Args:
        fig: Matplotlib figure
        email: Subscriber email
        
    Returns:
        Matplotlib figure with watermark
    """
    try:
        # Hash the email to add some privacy
        email_hash = hashlib.md5(email.encode()).hexdigest()[:8]
        
        # Add very light watermark text
        fig.text(0.5, 0.5, f"DailyStonks-{email_hash}", 
                fontsize=20, color='rgba(255,255,255,0.08)',
                ha='center', va='center', alpha=0.1,
                rotation=45, transform=fig.transFigure)
        
        return fig
    except Exception as e:
        logger.error(f"Error adding watermark: {e}")
        return fig  # Return original figure if watermarking fails

def send_report_email(html_content, subject="Daily Stock Market Report", images=None, recipients=None):
    """
    Send report email to one or more recipients (with rate limiting).
    
    Args:
        html_content (str): HTML content of the email
        subject (str): Email subject
        images (dict): Optional dict with {cid: image_bytes}
        recipients (list): List of email recipients
        
    Returns:
        bool: True if all emails were queued successfully
    """
    # Get email queue
    email_queue = EmailQueue()
    
    # Use environment variable if no recipients provided
    if recipients is None:
        recipients = os.environ.get('EMAIL_RECIPIENT', '').split(',')
    
    # Validate recipients
    valid_recipients = [email.strip() for email in recipients if email.strip()]
    if not valid_recipients:
        logger.error("No valid recipients provided")
        return False
    
    success = True
    for recipient in valid_recipients:
        # Queue email for sending
        if not email_queue.add_to_queue(recipient, subject, html_content, images, is_report=True):
            success = False
    
    return success

# Legacy function for compatibility
def send_email(subject, html_content, recipients=None, images=None):
    """
    Legacy function to maintain backward compatibility.
    """
    return send_report_email(html_content, subject, images, recipients)

# For testing
if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    
    # Test email
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Test Email</title>
    </head>
    <body>
        <h1>Test Email</h1>
        <p>This is a test email to verify that the email sending system is working.</p>
    </body>
    </html>
    """
    
    print("Sending test email...")
    result = send_report_email(test_html, "DailyStonks Test Email")
    print(f"Email queued: {result}")
    
    # Wait for email to be sent
    EmailQueue().wait_completion(timeout=30)
    print("Done!")