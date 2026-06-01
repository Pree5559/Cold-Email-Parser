import os
from dotenv import load_dotenv
from typing import Optional


class Config:
    """Configuration management for the cold email bot."""
    
    def __init__(self, env_file: str = ".env"):
        """Load configuration from environment variables."""
        load_dotenv(env_file)
        
        self.SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
        self.SMTP_USER: str = os.getenv("SMTP_USER", "")
        self.SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
        self.SENDER_NAME: str = os.getenv("SENDER_NAME", "")
        self.DRY_RUN: bool = os.getenv("DRY_RUN", "True").lower() == "true"
        
        self._validate()
    
    def _validate(self) -> None:
        """Validate required configuration values."""
        if not self.SMTP_USER:
            raise ValueError("SMTP_USER is required. Set it in your .env file.")
        
        if not self.SMTP_PASSWORD:
            raise ValueError("SMTP_PASSWORD is required. Set it in your .env file.")
        
        if not self.SENDER_NAME:
            raise ValueError("SENDER_NAME is required. Set it in your .env file.")
        
        if self.SMTP_PORT not in [587, 465]:
            raise ValueError(f"SMTP_PORT must be 587 (TLS) or 465 (SSL), got {self.SMTP_PORT}")
    
    def __repr__(self) -> str:
        """String representation of config (hiding sensitive data)."""
        return (
            f"Config(SMTP_HOST={self.SMTP_HOST}, "
            f"SMTP_PORT={self.SMTP_PORT}, "
            f"SMTP_USER={self.SMTP_USER[:3]}***@***, "
            f"SENDER_NAME={self.SENDER_NAME}, "
            f"DRY_RUN={self.DRY_RUN})"
        )
