# Architecture Document: The Closer - Cold Email Writer + Send Bot

## 1. System Overview

The Closer is a cold email automation system designed to help job seekers create and send personalized outreach emails at scale. The system follows a human-in-the-loop approach, ensuring that all emails are reviewed before sending to maintain quality and prevent spam.

### 1.1 System Purpose
- Generate personalized cold emails for job opportunities
- Automate email sending through Gmail or SMTP
- Maintain audit logs of all outreach activities
- Ensure human review before sending

### 1.2 Key Design Principles
- **Safety First**: Human review required before any email is sent
- **Simplicity**: Easy to understand and modify for educational purposes
- **Modularity**: Clear separation of concerns between components
- **Configurability**: Environment-based configuration for flexibility
- **Auditability**: Complete logging of all actions

---

## 2. High-Level Architecture

### 2.1 System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         The Closer System                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Input      │    │  Email       │    │   Email      │      │
│  │   Loader     │───▶│  Generator   │───▶│   Sender     │      │
│  │              │    │              │    │              │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         │                   ▼                   │               │
│         │            ┌──────────────┐           │               │
│         │            │   Preview    │           │               │
│         │            │   Handler    │           │               │
│         │            └──────────────┘           │               │
│         │                   │                   │               │
│         │                   ▼                   ▼               │
│         │            ┌──────────────┐    ┌──────────────┐      │
│         └───────────▶│    Logger    │◀───│   External   │      │
│                      │              │    │   Email API  │      │
│                      └──────────────┘    │   (Gmail/    │      │
│                                          │   SMTP)      │      │
│                                          └──────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Interaction Flow

1. **Input Loader** reads contact/job data from JSON, CSV, or hardcoded list
2. **Email Generator** creates personalized email content using templates
3. **Preview Handler** displays generated email for human review
4. **User confirms** via terminal prompt
5. **Email Sender** sends or drafts the email via Gmail API or SMTP
6. **Logger** records all actions to CSV log file
7. **External Email API** handles actual email delivery

---

## 3. Component Architecture

### 3.1 Input Loader Module

**Purpose**: Load and validate outreach target data

**Responsibilities**:
- Read contact data from multiple sources (JSON, CSV, hardcoded)
- Validate required fields
- Normalize data format
- Handle missing optional fields gracefully

**Input Formats**:
- JSON file (`contacts.json`)
- CSV file (`jobs.csv`)
- Python list (for demo purposes)

**Required Fields**:
- `recipient_email`
- `company`
- `role`
- `candidate_name`
- `candidate_background`

**Optional Fields**:
- `recipient_name`
- `job_url`
- `portfolio_url`
- `personalization_note`
- `linkedin_url`
- `resume_link`

**Interface**:
```python
class InputLoader:
    def load_from_json(self, filepath: str) -> List[Dict]
    def load_from_csv(self, filepath: str) -> List[Dict]
    def load_from_list(self, data: List[Dict]) -> List[Dict]
    def validate_record(self, record: Dict) -> bool
```

---

### 3.2 Email Generator Module

**Purpose**: Generate personalized cold email content

**Responsibilities**:
- Apply email template structure
- Inject personalization variables
- Generate subject lines
- Ensure email length constraints (<150 words)
- Validate email completeness

**Email Structure**:
1. **Subject Line**: Short, specific, role-related
2. **Personalization Hook**: Company/role-specific insight
3. **Introduction**: Who sender is and relevance
4. **Value Statement**: Connection to role
5. **Clear Ask**: Single action request
6. **Sign-off**: Name + links

**Template System**:
- Python f-string templates (MVP)
- Optional LLM-powered rewriting (stretch)
- Multiple template variations (stretch)

**Interface**:
```python
class EmailGenerator:
    def generate_email(self, record: Dict) -> Dict[str, str]
    def generate_subject(self, record: Dict) -> str
    def generate_body(self, record: Dict) -> str
    def validate_email(self, email: Dict) -> bool
    def count_words(self, text: str) -> int
```

---

### 3.3 Preview Handler Module

**Purpose**: Display generated email for human review

**Responsibilities**:
- Format email for terminal display
- Show all key fields clearly
- Highlight personalization elements
- Present confirmation options

**Display Format**:
```
═══════════════════════════════════════════════════════════
EMAIL PREVIEW
═══════════════════════════════════════════════════════════
To: priya@example.com (Priya Sharma)
Company: Acme AI
Role: Backend Engineering Intern

Subject: Quick note on the Backend Engineering Intern role

───────────────────────────────────────────────────────────────
Hi Priya,

I noticed Acme AI is hiring for Backend Engineering Intern. 
Company recently launched an AI workflow automation product.

I'm Your Name, and I've been building projects around Python 
developer interested in automation and AI agents.
The role stood out because it connects closely with my interest 
in practical automation and product-focused engineering.

Would you be open to a quick look at my profile or pointing me 
to the right person?

Best,
Your Name
https://github.com/yourname
───────────────────────────────────────────────────────────────

Send this email? (yes/no/skip):
```

**Interface**:
```python
class PreviewHandler:
    def display_email(self, email: Dict, record: Dict) -> None
    def get_confirmation(self) -> str
    def format_preview(self, email: Dict, record: Dict) -> str
```

---

### 3.4 Email Sender Module

**Purpose**: Send or draft emails via external email service

**Responsibilities**:
- Connect to email service (Gmail API or SMTP)
- Handle authentication
- Send emails or create drafts
- Handle send errors gracefully
- Support dry-run mode

**Sending Modes**:
- **Draft Mode**: Create Gmail drafts (safer, recommended)
- **Send Mode**: Direct send via SMTP or API

**Supported Services**:
- Gmail API (via MCP or direct)
- SMTP (smtplib)
- SendGrid (optional)
- Resend (optional)

**Interface**:
```python
class EmailSender:
    def __init__(self, config: Dict)
    def send_email(self, to: str, subject: str, body: str) -> bool
    def create_draft(self, to: str, subject: str, body: str) -> bool
    def authenticate(self) -> bool
    def handle_error(self, error: Exception) -> None
```

---

### 3.5 Logger Module

**Purpose**: Maintain audit trail of all outreach activities

**Responsibilities**:
- Log each email generation attempt
- Record send/draft status
- Track errors and failures
- Append to CSV log file
- Generate summary reports

**Log Entry Fields**:
- `timestamp`: ISO 8601 datetime
- `recipient_email`: Target email address
- `company`: Company name
- `role`: Job role title
- `subject`: Email subject line
- `status`: generated, drafted, sent, skipped, failed
- `error_message`: Error details if applicable
- `word_count`: Email body word count

**Log Format** (CSV):
```csv
timestamp,recipient_email,company,role,subject,status,error_message,word_count
2024-01-15T10:30:00,priya@example.com,Acme AI,Backend Engineering Intern,Quick note on the Backend Engineering Intern role,sent,,127
```

**Interface**:
```python
class Logger:
    def __init__(self, log_file: str)
    def log_entry(self, record: Dict, email: Dict, status: str, error: str = None) -> None
    def generate_summary(self) -> Dict
    def get_log_file(self) -> str
```

---

## 4. Data Architecture

### 4.1 Input Data Schema

```json
{
  "recipient_name": "string (optional)",
  "recipient_email": "string (required)",
  "company": "string (required)",
  "role": "string (required)",
  "job_url": "string (optional)",
  "personalization_note": "string (optional)",
  "candidate_name": "string (required)",
  "candidate_background": "string (required)",
  "portfolio_url": "string (optional)",
  "linkedin_url": "string (optional)",
  "resume_link": "string (optional)"
}
```

### 4.2 Email Data Schema

```python
{
  "to": "string",
  "subject": "string",
  "body": "string",
  "word_count": "int",
  "generated_at": "datetime"
}
```

### 4.3 Log Data Schema

```csv
timestamp,recipient_email,company,role,subject,status,error_message,word_count
```

### 4.4 Configuration Schema

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SENDER_NAME=Your Name
DRY_RUN=true
GMAIL_CLIENT_ID=  # Optional for Gmail API
GMAIL_CLIENT_SECRET=  # Optional for Gmail API
GMAIL_REFRESH_TOKEN=  # Optional for Gmail API
```

---

## 5. Technology Stack

### 5.1 Core Technologies

**Language**: Python 3.8+

**Rationale**:
- Simple syntax for live teaching
- Extensive email libraries
- Easy environment configuration
- Strong string manipulation capabilities

### 5.2 Dependencies

**Required**:
- `python-dotenv`: Environment variable management
- `smtplib`: Built-in Python SMTP library

**Optional**:
- `google-api-python-client`: Gmail API integration
- `google-auth-oauthlib`: Gmail authentication
- `sendgrid`: SendGrid API client
- `groq`: LLM-powered email rewriting
- `streamlit`: Web UI (stretch goal)

### 5.3 File Structure

```
the-closer/
│
├── main.py                 # Orchestration script
├── email_generator.py      # Email generation logic
├── email_sender.py         # Email sending logic
├── input_loader.py         # Data loading logic
├── preview_handler.py      # Preview and confirmation logic
├── logger.py               # Logging logic
├── config.py               # Configuration management
│
├── contacts.json           # Input data (JSON format)
├── jobs.csv                # Input data (CSV format)
├── outreach_log.csv        # Activity log
├── .env                    # Environment variables (not committed)
├── .env.example            # Environment template
├── requirements.txt        # Python dependencies
├── README.md               # Documentation
│
└── docs/                   # Additional documentation
    ├── problemStatement.md
    ├── architecture.md
    └── api_reference.md
```

---

## 6. Security Architecture

### 6.1 Authentication & Credentials

**Credential Storage**:
- All credentials stored in `.env` file
- `.env` never committed to version control
- `.env.example` provided as template
- App passwords used for Gmail SMTP

**Gmail App Passwords**:
- Generated via Google Account settings
- Specific to the application
- Revocable without affecting main password
- Required for SMTP authentication

### 6.2 Safety Guardrails

**Human-in-the-Loop**:
- All emails require preview before sending
- User must explicitly confirm each email
- Option to skip individual emails
- No batch sending without review

**Dry-Run Mode**:
- `DRY_RUN=true` by default
- Simulates sending without actual delivery
- Logs all actions as if sent
- Requires explicit override to disable

**Rate Limiting**:
- No built-in rate limiting (MVP)
- Relies on human pace for natural limiting
- Email provider rate limits apply automatically

### 6.3 Data Privacy

**Data Handling**:
- No data stored externally
- All data processed locally
- Logs stored locally only
- No third-party analytics

**PII Considerations**:
- Email addresses processed in memory
- No persistent PII beyond logs
- User responsible for log file security

---

## 7. Error Handling Architecture

### 7.1 Error Categories

**Input Errors**:
- Missing required fields
- Invalid email format
- File not found
- Malformed JSON/CSV

**Generation Errors**:
- Template rendering failure
- Missing personalization data
- Word count exceeded

**Sending Errors**:
- Authentication failure
- Network timeout
- SMTP server error
- Invalid recipient address

**Logging Errors**:
- File write permission
- Disk space exhausted
- CSV formatting error

### 7.2 Error Handling Strategy

**Graceful Degradation**:
- Continue processing remaining records on individual failures
- Log all errors with context
- Provide clear error messages
- Never crash silently

**Error Recovery**:
- Retry logic for transient errors
- Skip option for user on confirmation
- Detailed error logging for debugging

**User Communication**:
- Clear error messages in terminal
- Suggested fixes when possible
- Error codes for reference

---

## 8. Deployment Architecture

### 8.1 Local Development

**Environment Setup**:
```bash
# Clone repository
git clone <repo-url>
cd the-closer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run the application
python main.py
```

### 8.2 Production Considerations

**For Local Use** (MVP target):
- Run locally on user's machine
- No server deployment required
- User manages their own credentials
- Logs stored locally

**Potential Cloud Deployment** (future):
- Containerize with Docker
- Use secret management (AWS Secrets Manager, etc.)
- Deploy to cloud functions (AWS Lambda, etc.)
- Add web UI for remote access

---

## 9. Scalability Considerations

### 9.1 Current Limitations (MVP)

**Volume**:
- Designed for low-volume outreach (5-20 emails per session)
- No parallel processing
- Sequential email generation and sending

**Performance**:
- Template-based generation is fast
- SMTP sending limited by network latency
- Human review is the bottleneck

**Storage**:
- In-memory processing
- Local CSV logging
- No database

### 9.2 Future Scalability Options

**Horizontal Scaling**:
- Add worker queues for parallel processing
- Implement batch processing
- Add rate limiting and throttling

**Vertical Scaling**:
- Database for contact management
- Caching for template rendering
- Async I/O for email sending

**Feature Scaling**:
- LLM integration for dynamic generation
- A/B testing for email templates
- Analytics and response tracking

---

## 10. API Design (Future)

### 10.1 REST API Endpoints (Potential)

```
POST   /api/contacts          # Add new contact
GET    /api/contacts          # List all contacts
POST   /api/generate          # Generate email for contact
POST   /api/send              # Send generated email
POST   /api/draft             # Create draft
GET    /api/logs              # Retrieve activity logs
GET    /api/stats             # Get statistics
```

### 10.2 Webhook Integration (Potential)

```
POST   /webhook/email-sent    # Notification when email sent
POST   /webhook/email-failed  # Notification when email failed
POST   /webhook/reply         # Notification when reply received
```

---

## 11. Testing Strategy

### 11.1 Unit Tests

**Test Coverage**:
- Input validation
- Email generation
- Template rendering
- Word counting
- Log formatting

**Testing Framework**:
- `pytest` for test runner
- `unittest.mock` for mocking external services

### 11.2 Integration Tests

**Test Scenarios**:
- End-to-end workflow with mock email service
- File loading (JSON/CSV)
- Error handling paths
- Dry-run mode verification

### 11.3 Manual Testing

**Test Checklist**:
- Load sample contacts
- Generate emails
- Preview emails
- Send test email to self
- Verify log entries
- Check sent folder

---

## 12. Monitoring & Observability

### 12.1 Logging Levels

**DEBUG**: Detailed diagnostic information
**INFO**: Normal operation (email generated, sent)
**WARNING**: Non-critical issues (optional field missing)
**ERROR**: Failures (send failed, authentication error)

### 12.2 Metrics to Track

**Operational Metrics**:
- Emails generated
- Emails sent
- Emails drafted
- Emails skipped
- Error rate

**Quality Metrics**:
- Average word count
- Personalization usage rate
- Template variation usage

---

## 13. Extension Points

### 13.1 Template System

**Current**: Single Python f-string template
**Extension**: 
- Multiple template files
- Template selection logic
- A/B testing framework
- Template performance analytics

### 13.2 Email Generation

**Current**: Deterministic template
**Extension**:
- LLM-powered generation
- Tone adjustment
- Multi-language support
- Dynamic content insertion

### 13.3 Sending Methods

**Current**: SMTP or Gmail API
**Extension**:
- SendGrid integration
- Resend integration
- Multiple provider support
- Provider failover

### 13.4 User Interface

**Current**: Terminal-based
**Extension**:
- Streamlit web UI
- Desktop application
- Browser extension
- Mobile app

---

## 14. Compliance & Ethics

### 14.1 Anti-Spam Compliance

**CAN-SPAM Act**:
- Clear opt-out mechanism
- Accurate header information
- No misleading subject lines
- Physical address inclusion (if applicable)

**GDPR Considerations**:
- Data processing transparency
- Right to deletion
- Data minimization
- Consent management

### 14.2 Ethical Guidelines

**Transparency**:
- Use real sender identity
- No fake claims or relationships
- Clear purpose of outreach

**Respect**:
- Honor opt-out requests
- Personalize genuinely
- Avoid excessive frequency

**Quality**:
- Maintain high email quality
- Proofread before sending
- Relevant and valuable content

---

## 15. Implementation Phases

### Phase 1: MVP (Current Scope)
- Hardcoded input data
- Single template
- Terminal preview
- SMTP sending
- CSV logging
- Dry-run mode

### Phase 2: Enhanced Input
- JSON/CSV file loading
- Input validation
- Error handling
- Multiple data sources

### Phase 3: Advanced Features
- Gmail draft mode
- Multiple templates
- LLM integration
- Quality scoring

### Phase 4: Production Ready
- Web UI
- Database backend
- User authentication
- Analytics dashboard

---

## 16. Decision Log

### 16.1 Python over Node.js
**Decision**: Use Python
**Rationale**: 
- Simpler syntax for teaching
- Better string manipulation
- Built-in SMTP support
- Familiar to students

### 16.2 Terminal over Web UI
**Decision**: Terminal interface for MVP
**Rationale**:
- Faster to build live
- Easier to debug
- No frontend complexity
- Focus on core logic

### 16.3 CSV over Database
**Decision**: CSV logging
**Rationale**:
- No external dependencies
- Human-readable
- Easy to share
- Sufficient for MVP scale

### 16.4 SMTP over Gmail API
**Decision**: Support both, start with SMTP
**Rationale**:
- SMTP is simpler
- Works with any email provider
- Gmail API requires OAuth setup
- SMTP sufficient for MVP

---

## 17. Glossary

- **Cold Email**: Unsolicited email sent to a recipient with no prior contact
- **Personalization**: Customizing email content based on recipient-specific information
- **Dry Run**: Execution mode that simulates actions without actually performing them
- **Draft Mode**: Creating email drafts instead of sending immediately
- **Outreach**: Proactive communication for networking or opportunity seeking
- **Template**: Pre-defined email structure with variable placeholders
- **SMTP**: Simple Mail Transfer Protocol for email transmission
- **MCP**: Model Context Protocol for AI service integration

---

## 18. References

- Problem Statement: `docs/problemStatement.md`
- Python SMTP Documentation: https://docs.python.org/3/library/smtplib.html
- Gmail API Documentation: https://developers.google.com/gmail/api
- CAN-SPAM Act: https://ftc.gov/tips-advice/business-center/guidance/can-spam-act-compliance-guide-business

---

**Document Version**: 1.0  
**Last Updated**: 2024-01-15  
**Author**: Architecture Team  
**Status**: Draft
