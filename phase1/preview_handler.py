import sys
import os
from typing import Dict, Optional

# Add phase3 to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'phase3'))

from quality_scorer import QualityScorer
from spam_checker import SpamChecker


class PreviewHandler:
    """Handle email preview and user confirmation."""
    
    def __init__(self, enable_quality_scoring: bool = True, enable_spam_check: bool = True):
        """Initialize the preview handler.
        
        Args:
            enable_quality_scoring: Whether to display quality scores
            enable_spam_check: Whether to display spam risk
        """
        self.enable_quality_scoring = enable_quality_scoring
        self.enable_spam_check = enable_spam_check
        self.quality_scorer = QualityScorer() if enable_quality_scoring else None
        self.spam_checker = SpamChecker() if enable_spam_check else None
    
    def preview_email(self, record: Dict, email: Dict) -> None:
        """
        Display email preview in terminal.
        
        Args:
            record: Contact record
            email: Generated email with subject and body
        """
        # Print header
        print("\n" + "=" * 60)
        print("EMAIL PREVIEW")
        print("=" * 60)
        
        # Print recipient info
        recipient_name = record.get('recipient_name', 'N/A')
        recipient_email = record['recipient_email']
        company = record['company']
        role = record['role']
        
        print(f"To: {recipient_email} ({recipient_name})")
        print(f"Company: {company}")
        print(f"Role: {role}")
        print()
        
        # Print subject
        print(f"Subject: {email['subject']}")
        print()
        
        # Print body
        print("-" * 60)
        print(email['body'])
        print("-" * 60)
        print()
        
        # Print quality score if enabled
        if self.enable_quality_scoring and self.quality_scorer:
            self._display_quality_score(email)
        
        # Print spam risk if enabled
        if self.enable_spam_check and self.spam_checker:
            self._display_spam_risk(email)
    
    def get_confirmation(self) -> str:
        """
        Get user confirmation for sending email.
        
        Returns:
            'yes' to send, 'no' to skip, 'skip' to skip
        """
        while True:
            response = input("Send this email? (yes/no/skip): ").strip().lower()
            
            if response in ['yes', 'y']:
                return 'yes'
            elif response in ['no', 'n']:
                return 'no'
            elif response in ['skip', 's']:
                return 'skip'
            else:
                print("Invalid input. Please enter 'yes', 'no', or 'skip'.")
    
    def _display_quality_score(self, email: Dict) -> None:
        """Display email quality score."""
        score_result = self.quality_scorer.score_email(email)
        
        print("~" * 60)
        print("QUALITY SCORE")
        print("~" * 60)
        print(f"Overall Score: {score_result['overall_score']}/1.0")
        print(f"Word Count: {score_result['word_count']}")
        print()
        print("Breakdown:")
        for criterion, score in score_result['breakdown'].items():
            print(f"  {criterion}: {score}/1.0")
        
        if score_result['recommendations']:
            print()
            print("Recommendations:")
            for rec in score_result['recommendations']:
                print(f"  - {rec}")
        print("~" * 60)
        print()
    
    def _display_spam_risk(self, email: Dict) -> None:
        """Display spam risk assessment."""
        spam_result = self.spam_checker.check_spam_risk(email)
        
        print("~" * 60)
        print("SPAM RISK ASSESSMENT")
        print("~" * 60)
        print(f"Risk Level: {spam_result['risk_level']}")
        print(f"Risk Score: {spam_result['risk_score']}")
        
        if spam_result['issues']:
            print()
            print("Issues:")
            for issue in spam_result['issues']:
                print(f"  - {issue}")
        else:
            print("No spam indicators detected.")
        
        print("~" * 60)
        print()
    
    def display_summary(self, total: int, sent: int, skipped: int, failed: int) -> None:
        """
        Display summary of email sending session.
        
        Args:
            total: Total number of emails processed
            sent: Number of emails sent
            skipped: Number of emails skipped
            failed: Number of emails that failed
        """
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total emails: {total}")
        print(f"Sent: {sent}")
        print(f"Skipped: {skipped}")
        print(f"Failed: {failed}")
        print("=" * 60)
