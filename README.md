# The Closer - Cold Email Writer + Send Bot

A Python-based automation tool for generating and sending personalized cold emails for job applications.

## Features

- Generate personalized cold emails from contact data
- Preview emails before sending
- Send emails via SMTP (Gmail)
- Log all outreach activities to CSV
- Dry-run mode for testing

## Setup

### Prerequisites

- Python 3.8+
- Gmail account with App Password
- Virtual environment

### Installation

1. Create and activate virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Gmail credentials
```

### Gmail App Password Setup

1. Enable 2-Factor Authentication on your Google Account
2. Go to Google Account > Security > 2-Step Verification
3. Select "App passwords"
4. Create new app password (name it "The Closer")
5. Copy the 16-character app password to your `.env` file

## Usage

### Phase 1: MVP (Hardcoded Contacts)

Run the main script:
```bash
python phase1/main.py
```

This will:
- Load hardcoded sample contacts
- Generate personalized emails
- Preview each email
- Ask for confirmation before sending
- Log all actions to `outreach_log.csv`

### Dry Run Mode

By default, the bot runs in dry-run mode (no emails are sent). To actually send emails:

1. Set `DRY_RUN=False` in your `.env` file
2. Run the script again

## Project Structure

```
cold_email_parser/
├── phase0/          # Environment setup scripts
├── phase1/          # MVP Foundation
│   ├── config.py
│   ├── input_loader.py
│   ├── email_generator.py
│   ├── preview_handler.py
│   ├── email_sender.py
│   ├── logger.py
│   └── main.py
├── phase2/          # Enhanced Input & Validation
├── phase3/          # Advanced Features
├── phase4/          # Production Readiness
├── docs/            # Documentation
└── tests/           # Test files
```

## Logging

All outreach activities are logged to `outreach_log.csv` with the following columns:
- timestamp
- recipient_email
- company
- role
- subject
- status
- error_message
- word_count

## Troubleshooting

### SMTP Authentication Error
- Verify your Gmail App Password is correct
- Ensure 2FA is enabled on your Google Account
- Check that SMTP_USER is your full Gmail address

### Import Errors
- Ensure virtual environment is activated
- Verify all dependencies are installed: `pip install -r requirements.txt`

## License

MIT License
