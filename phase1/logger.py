import csv
from datetime import datetime
from typing import Dict, Optional
import os


class Logger:
    """Log email outreach activities to CSV file."""
    
    # Log file schema
    LOG_HEADERS = [
        "timestamp",
        "recipient_email",
        "company",
        "role",
        "subject",
        "status",
        "error_message",
        "word_count"
    ]
    
    def __init__(self, log_file: str = "outreach_log.csv"):
        """
        Initialize the logger.
        
        Args:
            log_file: Path to the log file
        """
        self.log_file = log_file
        self._initialize_log_file()
    
    def _initialize_log_file(self) -> None:
        """Create log file with headers if it doesn't exist."""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(self.LOG_HEADERS)
            print(f"Created log file: {self.log_file}")
    
    def log_entry(
        self,
        recipient_email: str,
        company: str,
        role: str,
        subject: str,
        status: str,
        error_message: Optional[str] = None,
        word_count: Optional[int] = None
    ) -> None:
        """
        Log an email outreach entry.
        
        Args:
            recipient_email: Recipient's email address
            company: Company name
            role: Job role
            subject: Email subject
            status: Status (sent, skipped, failed)
            error_message: Error message if failed
            word_count: Word count of email body
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        entry = {
            "timestamp": timestamp,
            "recipient_email": recipient_email,
            "company": company,
            "role": role,
            "subject": subject,
            "status": status,
            "error_message": error_message or "",
            "word_count": word_count or 0
        }
        
        with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.LOG_HEADERS)
            writer.writerow(entry)
        
        print(f"Logged entry: {recipient_email} - {status}")
    
    def log_sent(
        self,
        recipient_email: str,
        company: str,
        role: str,
        subject: str,
        word_count: int
    ) -> None:
        """Log a successfully sent email."""
        self.log_entry(
            recipient_email=recipient_email,
            company=company,
            role=role,
            subject=subject,
            status="sent",
            word_count=word_count
        )
    
    def log_skipped(
        self,
        recipient_email: str,
        company: str,
        role: str,
        subject: str,
        word_count: int
    ) -> None:
        """Log a skipped email."""
        self.log_entry(
            recipient_email=recipient_email,
            company=company,
            role=role,
            subject=subject,
            status="skipped",
            word_count=word_count
        )
    
    def log_failed(
        self,
        recipient_email: str,
        company: str,
        role: str,
        subject: str,
        error_message: str,
        word_count: int
    ) -> None:
        """Log a failed email send."""
        self.log_entry(
            recipient_email=recipient_email,
            company=company,
            role=role,
            subject=subject,
            status="failed",
            error_message=error_message,
            word_count=word_count
        )
