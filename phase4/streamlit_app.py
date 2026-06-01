import sys
import os
from typing import List, Dict, Optional
import streamlit as st
import pandas as pd

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'phase1'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'phase3'))

from phase1.config import Config
from phase1.input_loader import InputLoader
from phase1.email_generator import EmailGenerator
from phase1.email_sender import EmailSender
from phase1.logger import Logger
from phase3.quality_scorer import QualityScorer
from phase3.spam_checker import SpamChecker
from phase3.subject_generator import SubjectGenerator


# Page configuration
st.set_page_config(
    page_title="The Closer - Cold Email Bot",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .email-preview {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'config' not in st.session_state:
        try:
            st.session_state.config = Config()
        except Exception as e:
            st.session_state.config = None
            st.session_state.config_error = str(e)
    
    if 'contacts' not in st.session_state:
        st.session_state.contacts = []
    
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    
    if 'generated_emails' not in st.session_state:
        st.session_state.generated_emails = {}
    
    if 'log_entries' not in st.session_state:
        st.session_state.log_entries = []
    
    if 'template' not in st.session_state:
        st.session_state.template = "default"
    
    if 'use_llm' not in st.session_state:
        st.session_state.use_llm = False


def load_contacts_from_file(uploaded_file) -> List[Dict]:
    """Load contacts from uploaded file."""
    loader = InputLoader()
    
    if uploaded_file.name.endswith('.json'):
        # Save uploaded file temporarily
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        try:
            contacts = loader.load_from_json(temp_path)
            os.remove(temp_path)
            return contacts
        except Exception as e:
            os.remove(temp_path)
            raise e
    
    elif uploaded_file.name.endswith('.csv'):
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        try:
            contacts = loader.load_from_csv(temp_path)
            os.remove(temp_path)
            return contacts
        except Exception as e:
            os.remove(temp_path)
            raise e
    
    else:
        raise ValueError("Unsupported file format. Please upload JSON or CSV.")


def generate_email_for_contact(contact: Dict, template: str, use_llm: bool) -> Dict:
    """Generate email for a contact."""
    generator = EmailGenerator(template=template)
    email = generator.generate_email(contact)
    
    # Validate email
    is_valid, error_msg = generator.validate_email(email)
    
    if not is_valid:
        email['validation_error'] = error_msg
    
    # Get word count
    email['word_count'] = generator.get_word_count(email)
    
    # Quality scoring
    scorer = QualityScorer()
    quality_score = scorer.score_email(email)
    email['quality_score'] = quality_score
    
    # Spam check
    spam_checker = SpamChecker()
    spam_risk = spam_checker.check_spam_risk(email)
    email['spam_risk'] = spam_risk
    
    # LLM enhancement (optional)
    if use_llm:
        try:
            from phase3.llm_enhancer import LLMEmailEnhancer
            enhancer = LLMEmailEnhancer(st.session_state.config.GROQ_API_KEY)
            enhanced = enhancer.enhance_email(email['subject'], email['body'])
            email['original_subject'] = email['subject']
            email['original_body'] = email['body']
            email['subject'] = enhanced['subject']
            email['body'] = enhanced['body']
            email['llm_enhanced'] = True
        except Exception as e:
            email['llm_error'] = str(e)
            email['llm_enhanced'] = False
    
    return email


def send_email(contact: Dict, email: Dict) -> bool:
    """Send email via SMTP."""
    try:
        sender = EmailSender(st.session_state.config)
        sender.connect()
        
        success, error_msg = sender.send_email(
            to=contact['recipient_email'],
            subject=email['subject'],
            body=email['body']
        )
        
        sender.disconnect()
        if error_msg:
            st.warning(f"Note: {error_msg}")
        return success
    
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False


def log_action(contact: Dict, email: Dict, status: str, error: str = ""):
    """Log action to session state and CSV."""
    log_entry = {
        'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
        'recipient_email': contact['recipient_email'],
        'company': contact['company'],
        'role': contact['role'],
        'subject': email['subject'],
        'status': status,
        'error_message': error,
        'word_count': email.get('word_count', 0)
    }
    
    st.session_state.log_entries.append(log_entry)
    
    # Also log to CSV
    logger = Logger()
    logger.log_entry(
        recipient_email=contact['recipient_email'],
        company=contact['company'],
        role=contact['role'],
        subject=email['subject'],
        status=status,
        error_message=error,
        word_count=email.get('word_count', 0)
    )


def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">📧 The Closer - Cold Email Bot</h1>', unsafe_allow_html=True)
    
    # Check configuration
    if st.session_state.config is None:
        st.error(f"Configuration error: {st.session_state.config_error}")
        st.error("Please check your .env file and ensure all required fields are set.")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Template selection
        template_options = ["default", "direct", "story", "question", "value"]
        st.session_state.template = st.selectbox(
            "Email Template",
            template_options,
            index=template_options.index(st.session_state.template)
        )
        
        # LLM enhancement
        st.session_state.use_llm = st.checkbox(
            "Use LLM Enhancement (Groq API)",
            value=st.session_state.use_llm,
            help="Enhance emails using AI. Requires GROQ_API_KEY in .env"
        )
        
        # Dry run mode
        dry_run = st.checkbox(
            "Dry Run Mode",
            value=st.session_state.config.DRY_RUN,
            help="If enabled, emails won't actually be sent"
        )
        st.session_state.config.DRY_RUN = dry_run
        
        st.divider()
        
        # Stats
        st.header("📊 Statistics")
        if st.session_state.contacts:
            st.metric("Total Contacts", len(st.session_state.contacts))
            st.metric("Processed", st.session_state.current_index)
            sent_count = sum(1 for log in st.session_state.log_entries if log['status'] == 'sent')
            st.metric("Emails Sent", sent_count)
        
        st.divider()
        
        # Navigation
        st.header("🗺️ Navigation")
        if st.button("📁 Load Contacts"):
            st.session_state.show_upload = True
        if st.button("📧 Process Emails"):
            st.session_state.show_upload = False
        if st.button("📋 View Logs"):
            st.session_state.show_logs = True
    
    # Main content area
    if not st.session_state.contacts:
        st.info("👋 Welcome! Start by uploading your contacts file (JSON or CSV).")
        
        uploaded_file = st.file_uploader(
            "Upload Contacts",
            type=['json', 'csv'],
            help="Upload a JSON or CSV file with contact information"
        )
        
        if uploaded_file:
            try:
                with st.spinner("Loading contacts..."):
                    contacts = load_contacts_from_file(uploaded_file)
                    st.session_state.contacts = contacts
                    st.session_state.current_index = 0
                    st.success(f"✅ Successfully loaded {len(contacts)} contacts!")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error loading contacts: {str(e)}")
        
        # Show sample data option
        st.divider()
        st.subheader("Or use sample data")
        if st.button("Load Sample Contacts"):
            loader = InputLoader()
            st.session_state.contacts = loader.load_hardcoded_contacts()
            st.session_state.current_index = 0
            st.success(f"✅ Loaded {len(st.session_state.contacts)} sample contacts!")
            st.rerun()
    
    elif st.session_state.current_index < len(st.session_state.contacts):
        # Process current contact
        contact = st.session_state.contacts[st.session_state.current_index]
        
        # Generate email if not already generated
        if st.session_state.current_index not in st.session_state.generated_emails:
            with st.spinner("Generating email..."):
                email = generate_email_for_contact(
                    contact,
                    st.session_state.template,
                    st.session_state.use_llm
                )
                st.session_state.generated_emails[st.session_state.current_index] = email
        
        email = st.session_state.generated_emails[st.session_state.current_index]
        
        # Display contact info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Contact", contact.get('recipient_name', 'N/A'))
        with col2:
            st.metric("Company", contact['company'])
        with col3:
            st.metric("Role", contact['role'])
        
        st.divider()
        
        # Display email preview
        st.subheader("📧 Email Preview")
        
        # Quality indicators
        col1, col2, col3 = st.columns(3)
        with col1:
            quality_score = email.get('quality_score', {}).get('overall_score', 0)
            quality_score_pct = quality_score * 100 if quality_score < 1 else quality_score
            quality_color = "🟢" if quality_score_pct >= 80 else "🟡" if quality_score_pct >= 60 else "🔴"
            st.metric(f"Quality {quality_color}", f"{quality_score_pct:.0f}/100")
        
        with col2:
            word_count = email.get('word_count', 0)
            word_color = "🟢" if 50 <= word_count <= 150 else "🟡"
            st.metric(f"Words {word_color}", word_count)
        
        with col3:
            spam_risk = email.get('spam_risk', {}).get('risk_level', 'unknown')
            spam_color = "🟢" if spam_risk == 'low' else "🟡" if spam_risk == 'medium' else "🔴"
            st.metric(f"Spam Risk {spam_color}", spam_risk.capitalize())
        
        st.divider()
        
        # Email content
        st.markdown('<div class="email-preview">', unsafe_allow_html=True)
        st.text(f"Subject: {email['subject']}")
        st.text_area("Body:", email['body'], height=200, disabled=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Validation error
        if 'validation_error' in email:
            st.error(f"❌ Validation Error: {email['validation_error']}")
        
        # LLM enhancement notice
        if email.get('llm_enhanced'):
            st.info("✨ This email was enhanced using AI (Groq API)")
        
        # Action buttons
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📤 Send Email", type="primary", width='stretch'):
                if 'validation_error' in email:
                    st.error("❌ Cannot send email with validation errors")
                else:
                    with st.spinner("Sending email..."):
                        success = send_email(contact, email)
                        if success:
                            log_action(contact, email, 'sent')
                            st.success("✅ Email sent successfully!")
                            st.session_state.current_index += 1
                            st.rerun()
                        else:
                            log_action(contact, email, 'failed', 'Send error')
        
        with col2:
            if st.button("⏭️ Skip", width='stretch'):
                log_action(contact, email, 'skipped')
                st.session_state.current_index += 1
                st.rerun()
        
        with col3:
            if st.button("🔄 Regenerate", width='stretch'):
                del st.session_state.generated_emails[st.session_state.current_index]
                st.rerun()
        
        # Progress bar
        progress = (st.session_state.current_index + 1) / len(st.session_state.contacts)
        st.progress(progress, f"Processing {st.session_state.current_index + 1} of {len(st.session_state.contacts)}")
    
    else:
        # All contacts processed
        st.success("🎉 All contacts have been processed!")
        
        # Summary
        st.subheader("📊 Summary")
        
        sent_count = sum(1 for log in st.session_state.log_entries if log['status'] == 'sent')
        skipped_count = sum(1 for log in st.session_state.log_entries if log['status'] == 'skipped')
        failed_count = sum(1 for log in st.session_state.log_entries if log['status'] == 'failed')
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Sent", sent_count)
        with col2:
            st.metric("Skipped", skipped_count)
        with col3:
            st.metric("Failed", failed_count)
        
        # View logs
        if st.button("📋 View Full Logs"):
            st.session_state.show_logs = True
            st.rerun()
        
        # Reset
        if st.button("🔄 Start Over"):
            st.session_state.contacts = []
            st.session_state.current_index = 0
            st.session_state.generated_emails = {}
            st.session_state.log_entries = []
            st.rerun()
    
    # Show logs if requested
    if getattr(st.session_state, 'show_logs', False) and st.session_state.log_entries:
        st.divider()
        st.subheader("📋 Activity Logs")
        
        logs_df = pd.DataFrame(st.session_state.log_entries)
        st.dataframe(logs_df, width='stretch')
        
        # Download logs
        csv = logs_df.to_csv(index=False)
        st.download_button(
            "Download Logs (CSV)",
            csv,
            "outreach_log.csv",
            "text/csv"
        )
        
        if st.button("Close Logs"):
            st.session_state.show_logs = False
            st.rerun()


if __name__ == "__main__":
    main()
