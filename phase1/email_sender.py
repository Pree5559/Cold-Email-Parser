import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import sys


class EmailSender:
    """Send emails via SMTP with dry-run mode support."""
    
    def __init__(self, config):
        """
        Initialize the email sender.
        
        Args:
            config: Config object with SMTP settings
        """
        self.config = config
        self.smtp: Optional[smtplib.SMTP] = None
    
    def connect(self) -> None:
        """Establish SMTP connection."""
        if self.config.DRY_RUN:
            print("[DRY RUN] Skipping SMTP connection")
            return
        
        try:
            if self.config.SMTP_PORT == 587:
                # TLS connection
                self.smtp = smtplib.SMTP(self.config.SMTP_HOST, self.config.SMTP_PORT)
                self.smtp.starttls()
            elif self.config.SMTP_PORT == 465:
                # SSL connection
                self.smtp = smtplib.SMTP_SSL(self.config.SMTP_HOST, self.config.SMTP_PORT)
            else:
                raise ValueError(f"Unsupported SMTP port: {self.config.SMTP_PORT}")
            
            # Login
            self.smtp.login(self.config.SMTP_USER, self.config.SMTP_PASSWORD)
            print(f"Connected to SMTP server: {self.config.SMTP_HOST}")
        
        except Exception as e:
            raise ConnectionError(f"Failed to connect to SMTP server: {e}")
    
    def send_email(self, to: str, subject: str, body: str) -> tuple[bool, str]:
        """
        Send an email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            
        Returns:
            Tuple of (success, error_message)
        """
        if self.config.DRY_RUN:
            print(f"[DRY RUN] Would send email to: {to}")
            print(f"[DRY RUN] Subject: {subject}")
            return True, ""
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config.SENDER_NAME
            msg['To'] = to
            msg['Subject'] = subject
            
            # Attach body
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            self.smtp.send_message(msg)
            print(f"Email sent successfully to: {to}")
            return True, ""
        
        except Exception as e:
            error_msg = f"Failed to send email to {to}: {e}"
            print(f"ERROR: {error_msg}")
            return False, error_msg
    
    def disconnect(self) -> None:
        """Close SMTP connection."""
        if self.smtp:
            try:
                self.smtp.quit()
                print("SMTP connection closed")
            except Exception as e:
                print(f"Warning: Error closing SMTP connection: {e}")
            finally:
                self.smtp = None
