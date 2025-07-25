import os
import traceback
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from premailer import transform

def send_report_email(html_content, subject="Daily Stock Market Report", images=None):
    """
    Sends an HTML email with optional embedded images using CID.
    
    Args:
        html_content (str): HTML content with <img src="cid:..."> tags
        subject (str): Email subject
        images (dict): Optional {cid: image_bytes}
    """
    sender_email = os.environ.get('EMAIL_SENDER')
    sender_password = os.environ.get('EMAIL_PASSWORD')
    smtp_server = os.environ.get('EMAIL_SMTP')
    smtp_port = os.environ.get('EMAIL_PORT')
    recipients = os.environ.get('EMAIL_RECIPIENT', '').split(',')

    # Validate environment
    missing = [k for k, v in {
        'EMAIL_SENDER': sender_email,
        'EMAIL_PASSWORD': sender_password,
        'EMAIL_SMTP': smtp_server,
        'EMAIL_PORT': smtp_port,
        'EMAIL_RECIPIENT': recipients[0] if recipients else None
    }.items() if not v]

    if missing:
        print(f"Error: Missing required environment variables: {', '.join(missing)}")
        return False

    try:
        email_ready_html = transform(html_content)

        msg = MIMEMultipart('related')
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = ", ".join(recipients)
        msg['List-Unsubscribe'] = f"<https://whispr.dev/unsubscribe?email={recipients[0]}>"


        alt = MIMEMultipart('alternative')
        alt.attach(MIMEText(email_ready_html, 'html'))
        msg.attach(alt)

        if images:
            for cid, img_bytes in images.items():
                img = MIMEImage(img_bytes, 'png')
                img.add_header('Content-ID', f'<{cid}>')
                img.add_header('Content-Disposition', 'inline', filename=f'{cid}.png')
                msg.attach(img)

        server = smtplib.SMTP(smtp_server, int(smtp_port))
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipients, msg.as_string())
        server.quit()

        print("Email sent successfully with inline images.")
        return True

    except Exception as e:
        print(f"Email send failed: {e}")
        traceback.print_exc()
        return False
