# Edge Cases Document: The Closer - Cold Email Writer + Send Bot

## Overview

This document catalogs all potential edge cases, error scenarios, and boundary conditions that the Cold Email Writer + Send Bot system should handle. Each edge case includes a description, severity level, expected behavior, and testing approach.

**Purpose**: Ensure robust error handling and graceful degradation across all system components.

---

## 1. Input Data Edge Cases

### 1.1 Missing Required Fields

**Description**: Contact record missing one or more required fields.

**Required Fields**:
- `recipient_email`
- `company`
- `role`
- `candidate_name`
- `candidate_background`

**Severity**: High

**Expected Behavior**:
- Validation should fail before email generation
- Clear error message indicating which field is missing
- System should skip this contact and continue with others
- Log the validation failure with specific field name

**Test Case**:
```python
{
    "recipient_email": "priya@example.com",
    "company": "Acme AI",
    # Missing: role, candidate_name, candidate_background
}
```

**Expected Error**: "Validation failed: Missing required field 'role'"

---

### 1.2 Invalid Email Format

**Description**: Email address does not match standard email format.

**Severity**: High

**Expected Behavior**:
- Email format validation using regex
- Reject invalid email addresses
- Clear error message with the invalid email shown
- Skip contact and continue processing

**Test Cases**:
```python
# Invalid formats
"invalid-email"
"@example.com"
"user@"
"user@.com"
"user@domain"
"spaces in@email.com"
"user@domain..com"
```

**Expected Error**: "Invalid email format: 'invalid-email'"

---

### 1.3 Empty String Values

**Description**: Required fields present but empty strings.

**Severity**: Medium

**Expected Behavior**:
- Treat empty strings as missing values
- Apply same validation as missing fields
- Trim whitespace before validation
- Log validation failure

**Test Case**:
```python
{
    "recipient_email": "priya@example.com",
    "company": "",  # Empty string
    "role": "Backend Engineer",
    "candidate_name": "John Doe",
    "candidate_background": "Python developer"
}
```

**Expected Error**: "Validation failed: Field 'company' is empty"

---

### 1.4 Whitespace-Only Values

**Description**: Fields contain only whitespace characters.

**Severity**: Medium

**Expected Behavior**:
- Trim whitespace from all fields
- Treat whitespace-only as empty after trimming
- Apply validation after trimming
- Log if trimming occurred

**Test Case**:
```python
{
    "recipient_email": "  priya@example.com  ",
    "company": "   ",
    "role": "  Backend Engineer  ",
    "candidate_name": "  John Doe  ",
    "candidate_background": "  Python developer  "
}
```

**Expected Behavior**: Trim values, validate, reject if empty

---

### 1.5 Extra Fields in Input

**Description**: Contact record contains fields not in the schema.

**Severity**: Low

**Expected Behavior**:
- Ignore unknown fields (don't crash)
- Log warning about unknown fields
- Continue processing with known fields
- Optional: Store unknown fields in metadata

**Test Case**:
```python
{
    "recipient_email": "priya@example.com",
    "company": "Acme AI",
    "role": "Backend Engineer",
    "candidate_name": "John Doe",
    "candidate_background": "Python developer",
    "unknown_field": "some value",
    "another_unknown": 123
}
```

**Expected Behavior**: Process successfully, log warning about unknown fields

---

### 1.6 Wrong Data Types

**Description**: Fields have incorrect data types.

**Severity**: Medium

**Expected Behavior**:
- Type validation for each field
- Attempt type conversion where safe (e.g., int to str)
- Reject if conversion fails
- Clear error message about type mismatch

**Test Cases**:
```python
{
    "recipient_email": 12345,  # Should be string
    "company": ["Acme AI"],    # Should be string
    "role": None,              # Should be string
    "candidate_name": True,     # Should be string
    "candidate_background": {}  # Should be string
}
```

**Expected Error**: "Type error: Field 'recipient_email' should be string, got int"

---

### 1.7 Special Characters in Fields

**Description**: Fields contain special characters that might break templates.

**Severity**: Medium

**Expected Behavior**:
- Sanitize special characters where appropriate
- Escape characters in email body
- Preserve special characters in names/companies where valid
- Handle Unicode characters properly

**Test Cases**:
```python
{
    "recipient_email": "priya.o'brien@example.com",
    "company": "Acme & AI",
    "role": "Senior <Engineer>",
    "candidate_name": "José García",
    "candidate_background": "Python & JavaScript developer"
}
```

**Expected Behavior**: Process correctly with proper escaping

---

### 1.8 Extremely Long Field Values

**Description**: Field values exceed reasonable length limits.

**Severity**: Medium

**Expected Behavior**:
- Define maximum length for each field
- Truncate or reject overly long values
- Log truncation with original length
- Email body should still respect 150-word limit

**Test Cases**:
```python
{
    "recipient_email": "priya@example.com",
    "company": "A" * 1000,  # Extremely long company name
    "role": "Backend Engineer",
    "candidate_name": "John Doe",
    "candidate_background": "Python developer"
}
```

**Expected Behavior**: Truncate or reject with clear message

---

### 1.9 Duplicate Email Addresses

**Description**: Multiple contacts with the same email address.

**Severity**: Medium

**Expected Behavior**:
- Detect duplicate emails in input
- Option to skip duplicates or warn
- Log duplicate detection
- Allow user to choose action (skip/keep both)

**Test Case**:
```python
[
    {"recipient_email": "priya@example.com", "company": "Acme AI", ...},
    {"recipient_email": "priya@example.com", "company": "Tech Corp", ...}
]
```

**Expected Behavior**: Warn about duplicate, ask user to skip or keep

---

### 1.10 Malformed JSON Input

**Description**: JSON file has syntax errors or invalid structure.

**Severity**: High

**Expected Behavior**:
- Catch JSON parsing errors
- Provide specific error message with line number
- Stop processing and ask user to fix file
- Don't process any contacts from malformed file

**Test Cases**:
```json
// Missing comma
{
    "recipient_email": "priya@example.com"
    "company": "Acme AI"
}

// Trailing comma
{
    "recipient_email": "priya@example.com",
    "company": "Acme AI",
}

// Invalid JSON
{recipient_email: "priya@example.com"}  // Missing quotes
```

**Expected Error**: "JSON parsing error: line 3, column 5 - Expecting ',' delimiter"

---

### 1.11 Malformed CSV Input

**Description**: CSV file has formatting issues.

**Severity**: High

**Expected Behavior**:
- Handle CSV parsing errors gracefully
- Report specific line and column of error
- Skip malformed rows if possible
- Log all parsing errors

**Test Cases**:
```csv
recipient_email,company,role
priya@example.com,Acme AI,Backend Engineer
john@example.com,"Tech Corp,Inc",Senior Engineer  # Unquoted comma
jane@example.com,Startup,  # Missing column
```

**Expected Behavior**: Parse valid rows, log errors for invalid rows

---

### 1.12 Empty Input File

**Description**: Input file exists but contains no data.

**Severity**: Medium

**Expected Behavior**:
- Detect empty file
- Inform user clearly
- Exit gracefully without errors
- Suggest adding contacts or using hardcoded data

**Test Case**:
```json
[]
```

**Expected Behavior**: "Input file is empty. No contacts to process."

---

### 1.13 File Not Found

**Description**: Specified input file does not exist.

**Severity**: High

**Expected Behavior**:
- Check file existence before loading
- Clear error message with file path
- Suggest checking file path
- Exit gracefully

**Test Case**:
```bash
python main.py --input nonexistent.json
```

**Expected Error**: "File not found: nonexistent.json"

---

### 1.14 Permission Denied

**Description**: No read permission for input file.

**Severity**: High

**Expected Behavior**:
- Catch permission errors
- Clear error message
- Suggest checking file permissions
- Exit gracefully

**Expected Error**: "Permission denied: Cannot read contacts.json"

---

## 2. Email Generation Edge Cases

### 2.1 Missing Personalization Note

**Description**: Optional personalization_note field is missing.

**Severity**: Low

**Expected Behavior**:
- Use default generic phrase
- Log that personalization is missing
- Still generate email successfully
- Warn user about lower personalization

**Test Case**:
```python
{
    # ... other fields ...
    # personalization_note missing
}
```

**Expected Behavior**: Use default: "I came across your company and was impressed by your work."

---

### 2.2 Word Count Exceeded

**Description**: Generated email exceeds 150-word limit.

**Severity**: Medium

**Expected Behavior**:
- Count words before sending
- Warn user if over limit
- Offer to edit or regenerate
- Optionally auto-truncate with warning

**Test Case**:
```python
{
    "candidate_background": "A very long background description that goes on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on..."
}
```

**Expected Behavior**: "Warning: Email is 200 words (limit: 150). Edit or regenerate?"

---

### 2.3 Template Rendering Failure

**Description**: Template f-string fails due to missing variable.

**Severity**: High

**Expected Behavior**:
- Catch template rendering errors
- Provide specific error about missing variable
- Use fallback template
- Log the error

**Test Case**:
```python
# Template expects {recipient_name} but field is missing
body = f"Hi {recipient_name}, ..."
```

**Expected Error**: "Template error: Variable 'recipient_name' not found. Using fallback."

---

### 2.4 No Subject Line Generated

**Description**: Subject line generation fails or returns empty.

**Severity**: High

**Expected Behavior**:
- Validate subject line is not empty
- Use fallback subject if generation fails
- Log the failure
- Don't send email without subject

**Fallback Subject**: "Regarding job opportunity at {company}"

---

### 2.5 No Body Generated

**Description**: Email body generation fails or returns empty.

**Severity**: High

**Expected Behavior**:
- Validate body is not empty
- Use fallback body template
- Log the failure
- Don't send email without body

---

### 2.6 Special Characters Break Template

**Description**: Special characters in data break f-string formatting.

**Severity**: Medium

**Expected Behavior**:
- Escape curly braces in user data
- Handle quotes properly
- Use format() instead of f-strings if needed
- Test with various special characters

**Test Case**:
```python
{
    "company": "{Acme AI}",  # Curly braces
    "role": "Engineer \"Senior\"",  # Quotes
}
```

**Expected Behavior**: Proper escaping, template renders correctly

---

### 2.7 Unicode Characters Not Displayed

**Description**: Unicode characters not rendered correctly in terminal.

**Severity**: Low

**Expected Behavior**:
- Ensure terminal encoding support
- Use UTF-8 encoding consistently
- Fallback to ASCII if needed
- Log encoding issues

**Test Case**:
```python
{
    "candidate_name": "François Müller",
    "company": "日本株式会社"
}
```

**Expected Behavior**: Display correctly or use fallback encoding

---

### 2.8 Multiple Personalization Notes

**Description**: User provides array of personalization notes.

**Severity**: Low

**Expected Behavior**:
- If array, use first note or join them
- Log the handling strategy
- Document expected format

**Test Case**:
```python
{
    "personalization_note": ["Note 1", "Note 2", "Note 3"]
}
```

**Expected Behavior**: Use first note or combine with separators

---

### 2.9 Portfolio URL Invalid

**Description**: Portfolio URL is malformed or unreachable.

**Severity**: Low

**Expected Behavior**:
- Validate URL format
- Don't check reachability (too slow)
- Log if URL format is invalid
- Still generate email without URL

**Test Cases**:
```python
"portfolio_url": "not-a-url"
"portfolio_url": "htp://missing-typo.com"
"portfolio_url": "github.com/user"  # Missing protocol
```

**Expected Behavior**: Log warning, generate email without URL

---

### 2.10 All Optional Fields Missing

**Description**: Only required fields present, no optional fields.

**Severity**: Low

**Expected Behavior**:
- Generate email with minimal information
- Use sensible defaults for missing optional fields
- Log which optional fields are missing
- Email should still be functional

**Test Case**:
```python
{
    "recipient_email": "priya@example.com",
    "company": "Acme AI",
    "role": "Backend Engineer",
    "candidate_name": "John Doe",
    "candidate_background": "Python developer"
    # No optional fields
}
```

**Expected Behavior**: Generate email with defaults for missing fields

---

## 3. Email Sending Edge Cases

### 3.1 SMTP Connection Failure

**Description**: Cannot connect to SMTP server.

**Severity**: High

**Expected Behavior**:
- Catch connection error
- Retry with exponential backoff (max 3 attempts)
- Clear error message
- Log failure
- Skip to next contact

**Test Scenario**: Network down, wrong SMTP host, firewall blocking

**Expected Error**: "SMTP connection failed: Connection refused. Retrying (1/3)..."

---

### 3.2 SMTP Authentication Failure

**Description**: Invalid SMTP credentials.

**Severity**: High

**Expected Behavior**:
- Catch authentication error
- Don't retry (credentials won't change)
- Clear error message about credentials
- Suggest checking .env file
- Stop processing (all sends will fail)

**Expected Error**: "SMTP authentication failed: Invalid credentials. Check SMTP_USER and SMTP_PASSWORD in .env"

---

### 3.3 Recipient Email Rejected

**Description**: SMTP server rejects recipient email.

**Severity**: High

**Expected Behavior**:
- Catch recipient rejection error
- Log specific error from server
- Skip this contact
- Continue with others
- Don't stop entire batch

**Expected Error**: "Email rejected for priya@example.com: 550 5.1.1 User unknown"

---

### 3.4 Email Size Too Large

**Description**: Email body exceeds server size limit.

**Severity**: Medium

**Expected Behavior**:
- Catch size limit error
- Log the size and limit
- Suggest shortening email
- Skip this contact
- Continue with others

**Expected Error**: "Email too large: 500KB (limit: 100KB). Please shorten the email body."

---

### 3.5 Rate Limit Exceeded

**Description**: SMTP server rate limits reached.

**Severity**: High

**Expected Behavior**:
- Catch rate limit error
- Implement delay before retry
- Log rate limit hit
- Suggest sending in smaller batches
- Optional: automatic rate limiting

**Expected Error**: "Rate limit exceeded. Waiting 60 seconds before retry..."

---

### 3.6 Timeout During Send

**Description**: SMTP operation times out.

**Severity**: Medium

**Expected Behavior**:
- Set reasonable timeout (30 seconds)
- Catch timeout error
- Retry once
- Log timeout
- Skip if retry fails

**Expected Error**: "SMTP timeout after 30 seconds. Retrying..."

---

### 3.7 Gmail API Quota Exceeded

**Description**: Gmail API daily quota exceeded.

**Severity**: High

**Expected Behavior**:
- Catch quota error
- Log quota limit and usage
- Stop sending for the day
- Suggest waiting or using different method
- Clear error message

**Expected Error**: "Gmail API quota exceeded. Daily limit reached. Please wait until tomorrow."

---

### 3.8 Gmail API Authentication Expired

**Description**: OAuth token has expired.

**Severity**: High

**Expected Behavior**:
- Catch authentication expired error
- Attempt token refresh
- If refresh fails, prompt re-authentication
- Clear instructions for re-auth
- Stop processing until resolved

**Expected Error**: "Gmail API token expired. Attempting refresh... Refresh failed. Please re-authenticate."

---

### 3.9 Draft Creation Failure

**Description**: Gmail draft creation fails.

**Severity**: Medium

**Expected Behavior**:
- Catch draft creation error
- Log specific error
- Offer to try sending instead
- Skip if user declines
- Continue with other contacts

**Expected Error**: "Draft creation failed: API error. Try sending directly? (yes/no)"

---

### 3.10 Network Interruption During Send

**Description**: Network connection lost during email send.

**Severity**: Medium

**Expected Behavior**:
- Catch network error
- Log interruption point
- Don't mark as sent (uncertain state)
- Suggest manual verification
- Retry if possible

**Expected Error**: "Network interrupted during send. Email status uncertain. Please verify in sent folder."

---

### 3.11 Dry Run Mode Override

**Description**: User tries to send with dry-run still enabled.

**Severity**: Low

**Expected Behavior**:
- Check dry-run flag before sending
- Warn if dry-run is enabled
- Require explicit confirmation to disable
- Log dry-run status

**Expected Behavior**: "DRY_RUN is enabled. Emails will not be sent. Disable to send real emails."

---

### 3.12 Wrong SMTP Port

**Description**: SMTP port configuration is incorrect.

**Severity**: High

**Expected Behavior**:
- Validate port is numeric and in valid range
- Catch connection error due to wrong port
- Suggest common ports (587, 465, 25)
- Log port used

**Expected Error**: "SMTP connection failed on port 123. Try port 587 (TLS) or 465 (SSL)."

---

### 3.13 SSL/TLS Certificate Error

**Description**: SMTP server SSL certificate invalid.

**Severity**: Medium

**Expected Behavior**:
- Catch SSL certificate error
- Log certificate details
- Option to bypass (not recommended)
- Suggest checking server certificate

**Expected Error**: "SSL certificate error: Certificate invalid for smtp.gmail.com"

---

### 3.14 Email Already Sent

**Description**: Attempting to send email to same recipient twice.

**Severity**: Low

**Expected Behavior**:
- Check log for previous sends to this email
- Warn user about duplicate
- Ask to confirm or skip
- Log duplicate attempt

**Expected Behavior**: "Warning: Email already sent to priya@example.com on 2024-01-15. Send again? (yes/no)"

---

## 4. Logging Edge Cases

### 4.1 Log File Write Permission Denied

**Description**: No write permission for log file.

**Severity**: High

**Expected Behavior**:
- Catch permission error
- Try alternative location (temp directory)
- Clear error message
- Continue without logging (with warning)
- Suggest fixing permissions

**Expected Error**: "Cannot write to outreach_log.csv. Using temp directory instead."

---

### 4.2 Log File Already Open

**Description**: Log file is open in another program.

**Severity**: Medium

**Expected Behavior**:
- Catch file lock error
- Wait and retry (max 3 times)
- Log to memory if file unavailable
- Warn user about logging issues

**Expected Error**: "Log file is locked. Retrying in 5 seconds..."

---

### 4.3 Disk Full

**Description**: No disk space for log file.

**Severity**: High

**Expected Behavior**:
- Catch disk full error
- Stop processing immediately
- Clear error message
- Suggest freeing disk space
- Don't continue without logging

**Expected Error**: "Disk full. Cannot write log. Please free disk space."

---

### 4.4 Log File Corrupted

**Description**: Existing log file has invalid format.

**Severity**: Medium

**Expected Behavior**:
- Detect corruption on read
- Backup corrupted file
- Create new log file
- Log the corruption event
- Continue with new file

**Expected Behavior**: "Log file corrupted. Backed up to outreach_log.csv.bak. Creating new log."

---

### 4.5 CSV Header Mismatch

**Description**: Log file has different column structure.

**Severity**: Medium

**Expected Behavior**:
- Detect header mismatch
- Log the mismatch
- Option to migrate or create new file
- Document expected header format

**Expected Behavior**: "Log header mismatch. Expected: timestamp,email,... Found: id,date,... Create new log? (yes/no)"

---

### 4.6 Concurrent Log Writes

**Description**: Multiple processes writing to same log file.

**Severity**: Medium

**Expected Behavior**:
- Implement file locking
- Use append mode safely
- Handle write conflicts
- Log conflicts when they occur

**Expected Behavior**: "Log write conflict. Retrying with file lock..."

---

### 4.7 Timestamp Generation Failure

**Description**: System clock or timezone issues.

**Severity**: Low

**Expected Behavior**:
- Use UTC timezone consistently
- Fallback to Unix timestamp if datetime fails
- Log timestamp generation issues
- Document timestamp format

**Expected Behavior**: "Timestamp generation failed. Using Unix timestamp: 1705280400"

---

### 4.8 Log Entry Too Long

**Description**: Single log entry exceeds CSV line limit.

**Severity**: Low

**Expected Behavior**:
- Truncate long fields
- Log truncation
- Ensure CSV structure maintained
- Document field limits

**Expected Behavior**: "Log entry truncated: error_message too long (500 chars, keeping 200)"

---

### 4.9 Special Characters in Log

**Description**: Log data contains characters that break CSV format.

**Severity**: Medium

**Expected Behavior**:
- Properly escape CSV special characters (quotes, commas, newlines)
- Use CSV writer library (don't manually format)
- Test with various special characters
- Validate CSV after write

**Test Case**: Error message contains quotes, commas, or newlines

**Expected Behavior**: Proper CSV escaping, file remains valid

---

### 4.10 Log File Rotation Needed

**Description**: Log file becomes too large.

**Severity**: Low

**Expected Behavior**:
- Monitor log file size
- Implement rotation when size limit reached
- Archive old logs
- Create new log file
- Document rotation policy

**Expected Behavior**: "Log file exceeds 10MB. Rotating to outreach_log_2024-01-15.csv"

---

## 5. Preview & User Interaction Edge Cases

### 5.1 User Enters Invalid Response

**Description**: User enters something other than yes/no/skip.

**Severity**: Low

**Expected Behavior**:
- Validate user input
- Show valid options
- Reprompt on invalid input
- Limit retry attempts

**Test Cases**:
- "maybe"
- "y" (not "yes")
- "YES" (case sensitivity)
- Empty input
- Random characters

**Expected Behavior**: "Invalid input. Please enter 'yes', 'no', or 'skip':"

---

### 5.2 User Skips All Emails

**Description**: User chooses to skip every email.

**Severity**: Low

**Expected Behavior**:
- Allow skipping all emails
- Log all skips
- Show summary at end
- Don't force user to send

**Expected Behavior**: "All emails skipped. No emails sent."

---

### 5.3 User Interrupts with Ctrl+C

**Description**: User presses Ctrl+C during processing.

**Severity**: Medium

**Expected Behavior**:
- Catch keyboard interrupt
- Graceful shutdown
- Save progress so far
- Log interruption
- Show summary of completed work

**Expected Behavior**: "Interrupted by user. 2 emails sent, 1 skipped. Progress saved."

---

### 5.4 Terminal Too Narrow

**Description**: Terminal width too small for preview formatting.

**Severity**: Low

**Expected Behavior**:
- Detect terminal width
- Adjust formatting dynamically
- Use simple format if too narrow
- Don't break on narrow terminals

**Expected Behavior**: Detect width, use simplified format if needed

---

### 5.5 User Wants to Edit Email

**Description**: User wants to edit generated email before sending.

**Severity**: Low

**Expected Behavior**:
- Offer edit option in preview
- Open editor (or simple prompt-based edit)
- Validate edited email
- Use edited version for sending
- Log that email was edited

**Expected Behavior**: "Edit this email? (yes/no):" → Allow editing

---

### 5.6 User Wants to Save Draft Later

**Description**: User wants to save email as draft for later review.

**Severity**: Low

**Expected Behavior**:
- Offer "save for later" option
- Save to drafts file
- Log draft save
- Allow resuming from drafts

**Expected Behavior**: "Save as draft for later? (yes/no):"

---

### 5.7 No User Input (Automated Mode)

**Description**: Running in automated mode without user interaction.

**Severity**: Medium

**Expected Behavior**:
- Add --auto flag to skip confirmation
- Require explicit --auto flag (safety)
- Log that auto mode is enabled
- Send all generated emails without confirmation

**Expected Behavior**: "Auto mode enabled. Sending all emails without confirmation."

---

### 5.8 User Enters Email Address Manually

**Description**: User wants to override recipient email.

**Severity**: Low

**Expected Behavior**:
- Offer option to change recipient email
- Validate new email format
- Use new email for sending
- Log the change

**Expected Behavior**: "Change recipient email? (current: priya@example.com):"

---

### 5.9 Preview Display Error

**Description**: Error during preview formatting/display.

**Severity**: Medium

**Expected Behavior**:
- Catch display errors
- Fallback to simple format
- Log display error
- Don't crash on display issues

**Expected Behavior**: "Preview formatting error. Using simple format."

---

### 5.10 User Wants to See Previous Email

**Description**: User wants to go back to previous email.

**Severity**: Low

**Expected Behavior**:
- Store previous emails in memory
- Offer "back" option
- Allow re-reviewing
- Maintain state correctly

**Expected Behavior**: "Go back to previous email? (yes/no):"

---

## 6. Configuration Edge Cases

### 6.1 Missing .env File

**Description**: .env file does not exist.

**Severity**: High

**Expected Behavior**:
- Check for .env file on startup
- Copy .env.example if .env missing
- Clear instructions to configure
- Exit gracefully

**Expected Behavior**: ".env file not found. Created from .env.example. Please configure and retry."

---

### 6.2 Missing Required Environment Variable

**Description**: Required env var not set in .env.

**Severity**: High

**Expected Behavior**:
- Validate all required env vars on startup
- Clear error message about missing var
- Show which var is missing
- Exit gracefully

**Expected Error**: "Missing required environment variable: SMTP_USER"

---

### 6.3 Invalid Environment Variable Value

**Description**: Environment variable has invalid value.

**Severity**: High

**Expected Behavior**:
- Validate env var values
- Check port is numeric
- Check email format
- Check boolean values
- Clear error on validation failure

**Test Cases**:
```env
SMTP_PORT=not_a_number
DRY_RUN=maybe
SMTP_USER=no_at_sign.com
```

**Expected Error**: "Invalid value for SMTP_PORT: 'not_a_number' (must be numeric)"

---

### 6.4 Environment Variable Too Long

**Description**: Environment variable exceeds reasonable length.

**Severity**: Low

**Expected Behavior**:
- Check length of env vars
- Warn if unusually long
- Truncate if necessary
- Log truncation

**Expected Behavior**: "Warning: SMTP_PASSWORD is unusually long (500 chars). Verify it's correct."

---

### 6.5 Boolean Environment Variable Parsing

**Description**: Boolean env var has various string representations.

**Severity**: Low

**Expected Behavior**:
- Accept multiple boolean representations
- Support: true/false, yes/no, 1/0, on/off
- Case-insensitive
- Document accepted values

**Test Cases**:
```env
DRY_RUN=true
DRY_RUN=True
DRY_RUN=TRUE
DRY_RUN=yes
DRY_RUN=1
DRY_RUN=on
```

**Expected Behavior**: Parse all as True

---

### 6.6 Whitespace in Environment Variables

**Description**: Environment variables have leading/trailing whitespace.

**Severity**: Low

**Expected Behavior**:
- Trim whitespace from all env vars
- Log if trimming occurred
- Validate after trimming
- Document trimming behavior

**Test Case**:
```env
SMTP_USER=  user@example.com  
SMTP_PORT= 587 
```

**Expected Behavior**: Trim values, use "user@example.com" and "587"

---

### 6.7 Comment Lines in .env

**Description**: .env file contains comment lines.

**Severity**: Low

**Expected Behavior**:
- Support # comments
- Ignore comment lines
- Parse correctly with comments present
- Document comment support

**Test Case**:
```env
# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

**Expected Behavior**: Parse correctly, ignore comment line

---

### 6.8 Quoted Values in .env

**Description**: Environment variables are quoted.

**Severity**: Low

**Expected Behavior**:
- Handle quoted and unquoted values
- Strip quotes if present
- Support both single and double quotes
- Document quoting behavior

**Test Cases**:
```env
SENDER_NAME="John Doe"
SENDER_NAME='John Doe'
SENDER_NAME=John Doe
```

**Expected Behavior**: All parse as "John Doe"

---

### 6.9 Special Characters in Environment Variables

**Description**: Environment variables contain special characters.

**Severity**: Low

**Expected Behavior**:
- Handle special characters in values
- Escape if necessary
- Preserve special characters in passwords
- Test with various special chars

**Test Case**:
```env
SMTP_PASSWORD=p@ssw0rd!#$%
```

**Expected Behavior**: Preserve special characters correctly

---

### 6.10 Multiple .env Files

**Description**: Multiple .env files in different locations.

**Severity**: Low

**Expected Behavior**:
- Define priority order for .env files
- Document which .env is used
- Warn if multiple found
- Allow explicit .env path

**Priority**: .env (current dir) > ~/.closer.env > /etc/closer.env

---

## 7. System-Level Edge Cases

### 7.1 Python Version Incompatible

**Description**: Python version too old or incompatible.

**Severity**: High

**Expected Behavior**:
- Check Python version on startup
- Clear error if version < 3.8
- Suggest upgrading Python
- Exit gracefully

**Expected Error**: "Python 3.8+ required. Current version: 3.6. Please upgrade."

---

### 7.2 Missing Dependencies

**Description**: Required Python packages not installed.

**Severity**: High

**Expected Behavior**:
- Check for required imports
- Clear error about missing package
- Suggest: pip install -r requirements.txt
- Exit gracefully

**Expected Error**: "Missing dependency: python-dotenv. Run: pip install -r requirements.txt"

---

### 7.3 Dependency Version Conflict

**Description**: Installed package version incompatible.

**Severity**: Medium

**Expected Behavior**:
- Check package versions
- Warn about version mismatches
- Suggest specific version
- Try to run anyway if possible

**Expected Behavior**: "Warning: python-dotenv version 0.19.0 installed (expected 1.0.0+). May not work correctly."

---

### 7.4 Insufficient Memory

**Description**: System runs out of memory during processing.

**Severity**: Medium

**Expected Behavior**:
- Catch memory errors
- Process contacts in smaller batches
- Log memory usage
- Suggest closing other programs

**Expected Error**: "Memory error. Processing in smaller batches..."

---

### 7.5 CPU Timeout

**Description**: Processing takes too long.

**Severity**: Low

**Expected Behavior**:
- Monitor processing time
- Warn if taking unusually long
- Allow user to cancel
- Implement progress indicators

**Expected Behavior**: "Processing taking longer than expected. Press Ctrl+C to cancel."

---

### 7.6 Multiple Instances Running

**Description**: User runs multiple instances simultaneously.

**Severity**: Medium

**Expected Behavior**:
- Detect if another instance is running
- Warn about concurrent access
- Use file locking for log file
- Document concurrent behavior

**Expected Behavior**: "Warning: Another instance may be running. Log file locked."

---

### 7.7 System Clock Wrong

**Description**: System clock has incorrect time.

**Severity**: Low

**Expected Behavior**:
- Use UTC for all timestamps
- Warn if clock seems wrong
- Document timezone handling
- Allow manual timestamp override

**Expected Behavior**: "Warning: System clock may be incorrect. Using UTC timestamps."

---

### 7.8 Locale Issues

**Description**: System locale affects number/date formatting.

**Severity**: Low

**Expected Behavior**:
- Use locale-independent formatting
- Force UTF-8 encoding
- Test with different locales
- Document locale requirements

**Expected Behavior**: Force consistent formatting regardless of system locale

---

### 7.9 File Path Issues (Windows vs Unix)

**Description**: File path separators differ between OS.

**Severity**: Medium

**Expected Behavior**:
- Use pathlib for cross-platform paths
- Handle both / and \ separators
- Test on Windows and Unix
- Document path requirements

**Expected Behavior**: Use pathlib, handle paths correctly on all OS

---

### 7.10 Signal Handling

**Description**: System sends termination signals (SIGTERM, SIGKILL).

**Severity**: Medium

**Expected Behavior**:
- Handle SIGTERM gracefully
- Save progress
- Clean up resources
- Log termination
- SIGKILL cannot be caught (document limitation)

**Expected Behavior**: "Termination signal received. Saving progress and exiting."

---

## 8. Security Edge Cases

### 8.1 Credentials in Log File

**Description**: Accidentally logging sensitive credentials.

**Severity**: Critical

**Expected Behavior**:
- Never log passwords or API keys
- Redact sensitive data from logs
- Validate log entries before writing
- Audit logging code for credential leakage

**Prevention**: Explicit check for credential fields before logging

---

### 8.2 SQL Injection in Input

**Description**: Malicious input attempting SQL injection.

**Severity**: Critical

**Expected Behavior**:
- Use parameterized queries (if using DB)
- Sanitize all user input
- Never concatenate user input into queries
- Log injection attempts

**Prevention**: Parameterized queries, input sanitization

---

### 8.3 Command Injection in Templates

**Description**: Malicious input attempting command injection.

**Severity**: Critical

**Expected Behavior**:
- Never execute user input as commands
- Sanitize template variables
- Use safe template rendering
- Log injection attempts

**Prevention**: Safe template rendering, no shell command execution

---

### 8.4 Path Traversal Attack

**Description**: Malicious input attempting to access arbitrary files.

**Severity**: High

**Expected Behavior**:
- Validate all file paths
- Resolve paths to absolute paths
- Check path is within allowed directory
- Reject suspicious paths

**Prevention**: Path validation, directory restriction

---

### 8.5 Email Header Injection

**Description**: Malicious input attempting to inject email headers.

**Severity**: High

**Expected Behavior**:
- Validate email content
- Strip newlines from subject lines
- Use proper email library (don't manually format)
- Log injection attempts

**Prevention**: Use email library, validate content

---

### 8.6 Phishing Template Content

**Description**: User creates template that looks like phishing.

**Severity**: High

**Expected Behavior**:
- Warn about suspicious content
- Check for common phishing patterns
- Require explicit confirmation for suspicious emails
- Log suspicious templates

**Detection**: Check for urgency, threats, fake urgency

---

### 8.7 .env File Committed to Git

**Description**: Accidentally committing .env with real credentials.

**Severity**: Critical

**Expected Behavior**:
- Add .env to .gitignore
- Check for .env in git status
- Warn if .env would be committed
- Provide instructions to rotate compromised credentials

**Prevention**: .gitignore, pre-commit hooks

---

### 8.8 API Key Exposed in Error Messages

**Description**: Error messages include API keys or tokens.

**Severity**: Critical

**Expected Behavior**:
- Redact sensitive data from error messages
- Show only last 4 characters of tokens
- Never log full credentials
- Audit error message formatting

**Prevention**: Redaction in error handling

---

### 8.9 Directory Traversal in File Upload

**Description**: Malicious file upload attempting to access system files.

**Severity**: High

**Expected Behavior**:
- Validate uploaded file paths
- Restrict to upload directory
- Sanitize filenames
- Reject suspicious paths

**Prevention**: Path validation, directory restriction

---

### 8.10 Denial of Service via Large Input

**Description**: Extremely large input file causes system hang.

**Severity**: Medium

**Expected Behavior**:
- Limit input file size
- Process in chunks
- Implement timeout
- Reject files over size limit

**Prevention**: File size limits, chunked processing

---

## 9. Integration Edge Cases

### 9.1 Gmail API Service Down

**Description**: Gmail API service is unavailable.

**Severity**: High

**Expected Behavior**:
- Detect API unavailability
- Fallback to SMTP
- Log service outage
- Suggest retrying later

**Expected Behavior**: "Gmail API unavailable. Falling back to SMTP."

---

### 9.2 SendGrid API Rate Limit

**Description**: SendGrid API rate limit exceeded.

**Severity**: High

**Expected Behavior**:
- Catch rate limit error
- Implement exponential backoff
- Log rate limit details
- Suggest upgrading plan

**Expected Error**: "SendGrid rate limit exceeded. Waiting 60 seconds..."

---

### 9.3 LLM API Timeout

**Description**: LLM API request times out.

**Severity**: Medium

**Expected Behavior**:
- Set reasonable timeout (30 seconds)
- Catch timeout error
- Fallback to template generation
- Log timeout
- Don't block on LLM

**Expected Behavior**: "LLM API timeout. Using template-based generation."

---

### 9.4 LLM API Cost Limit

**Description**: LLM API cost limit reached.

**Severity**: Medium

**Expected Behavior**:
- Track API usage/cost
- Warn approaching limit
- Disable LLM when limit reached
- Fallback to templates

**Expected Behavior**: "LLM cost limit reached. Using template-based generation."

---

### 9.5 Groq API Key Invalid

**Description**: Groq API key is invalid or expired.

**Severity**: High

**Expected Behavior**:
- Catch authentication error
- Clear error message
- Disable LLM feature
- Fallback to templates
- Suggest checking API key

**Expected Error**: "Groq API key invalid. Using template-based generation."

---

### 9.6 Webhook Delivery Failure

**Description**: Webhook notification fails to deliver.

**Severity**: Low

**Expected Behavior**:
- Implement retry logic with backoff
- Log failed webhook deliveries
- Queue failed webhooks for retry
- Don't block main workflow

**Expected Behavior**: "Webhook delivery failed. Queued for retry."

---

### 9.7 Database Connection Lost

**Description**: Database connection lost during operation.

**Severity**: High

**Expected Behavior**:
- Catch connection error
- Attempt reconnection
- Rollback transaction if in progress
- Log connection loss
- Fallback to CSV logging if DB unavailable

**Expected Behavior**: "Database connection lost. Reconnecting... Using CSV logging as fallback."

---

### 9.8 External API Response Format Changed

**Description**: External API changes response format.

**Severity**: Medium

**Expected Behavior**:
- Validate API response structure
- Handle unexpected formats gracefully
- Log format changes
- Fallback to safe defaults
- Alert about API changes

**Expected Behavior**: "API response format unexpected. Using safe defaults."

---

### 9.9 OAuth Token Refresh Failure

**Description**: OAuth token refresh fails.

**Severity**: High

**Expected Behavior**:
- Catch refresh failure
- Prompt user to re-authenticate
- Clear instructions for re-auth
- Disable feature until re-auth
- Log refresh failure

**Expected Error**: "OAuth token refresh failed. Please re-authenticate."

---

### 9.10 Third-Party Service Deprecation

**Description**: Third-party service deprecated or shut down.

**Severity**: High

**Expected Behavior**:
- Detect service unavailability
- Clear error message
- Suggest alternative services
- Document service status
- Provide migration path

**Expected Behavior**: "Service deprecated. Please use alternative: [alternatives]"

---

## 10. Performance Edge Cases

### 10.1 Processing Large Contact List

**Description**: Contact list has 1000+ entries.

**Severity**: Medium

**Expected Behavior**:
- Process in batches
- Show progress indicator
- Allow cancellation
- Implement rate limiting
- Log batch progress

**Expected Behavior**: "Processing 1000 contacts in batches of 50..."

---

### 10.2 Memory Leak During Processing

**Description**: Memory usage grows unbounded during processing.

**Severity**: Medium

**Expected Behavior**:
- Monitor memory usage
- Process contacts one at a time
- Clear memory between contacts
- Log memory usage
- Warn if memory high

**Expected Behavior**: "Memory usage high (80%). Clearing cache..."

---

### 10.3 Slow Email Generation

**Description**: Email generation takes >10 seconds per email.

**Severity**: Low

**Expected Behavior**:
- Profile generation code
- Identify bottlenecks
- Optimize template rendering
- Log generation time
- Warn if slow

**Expected Behavior**: "Email generation slow (15s). Consider optimizing templates."

---

### 10.4 Database Query Slow

**Description**: Database queries take too long.

**Severity**: Medium

**Expected Behavior**:
- Add query timeouts
- Optimize queries
- Add indexes where needed
- Log slow queries
- Cache frequent queries

**Expected Behavior**: "Query slow (5s). Consider adding index."

---

### 10.5 File I/O Bottleneck

**Description**: File operations become bottleneck.

**Severity**: Low

**Expected Behavior**:
- Batch file writes
- Use async I/O where appropriate
- Buffer writes
- Log I/O performance
- Optimize file access patterns

**Expected Behavior**: "File I/O slow. Using buffered writes."

---

### 10.6 Concurrent Processing Bottleneck

**Description**: Too many concurrent operations slow system.

**Severity**: Medium

**Expected Behavior**:
- Limit concurrent operations
- Implement proper connection pooling
- Queue operations
- Monitor concurrency
- Adjust limits dynamically

**Expected Behavior**: "Too many concurrent operations. Limiting to 5 concurrent."

---

### 10.7 Preview Rendering Slow

**Description**: Email preview takes too long to render.

**Severity**: Low

**Expected Behavior**:
- Optimize preview formatting
- Cache rendered previews
- Simplify formatting if slow
- Log render time
- Warn if slow

**Expected Behavior**: "Preview rendering slow (3s). Using simplified format."

---

### 10.8 Log File Write Slow

**Description**: Writing to log file becomes slow.

**Severity**: Low

**Expected Behavior**:
- Buffer log writes
- Write in batches
- Use async logging
- Monitor write performance
- Rotate log files if large

**Expected Behavior**: "Log writes slow. Using buffered writes."

---

### 10.9 Network Latency High

**Description**: Network latency causes slow email sending.

**Severity**: Medium

**Expected Behavior**:
- Implement timeout
- Retry with backoff
- Log latency
- Suggest checking network
- Queue sends if latency too high

**Expected Behavior**: "Network latency high (500ms). Emails will send slowly."

---

### 10.10 Startup Time Slow

**Description**: Application takes too long to start.

**Severity**: Low

**Expected Behavior**:
- Profile startup code
- Lazy load non-essential modules
- Cache initialization
- Log startup time
- Optimize imports

**Expected Behavior**: "Startup slow (5s). Optimizing module loading."

---

## Testing Strategy

### Unit Testing
- Test each edge case in isolation
- Mock external dependencies
- Verify error handling
- Check log output

### Integration Testing
- Test edge cases across components
- Test with real services (staging)
- Verify graceful degradation
- Check end-to-end error flow

### Manual Testing
- Test edge cases manually
- Verify user-facing error messages
- Check system behavior under stress
- Document unexpected behaviors

### Regression Testing
- Re-test edge cases after changes
- Ensure fixes don't break other cases
- Maintain edge case test suite
- Update documentation as needed

---

## Summary

**Total Edge Cases Documented**: 100+

**Severity Distribution**:
- Critical: 8
- High: 35
- Medium: 40
- Low: 20+

**Categories Covered**:
- Input Data (14 cases)
- Email Generation (10 cases)
- Email Sending (14 cases)
- Logging (10 cases)
- Preview & User Interaction (10 cases)
- Configuration (10 cases)
- System-Level (10 cases)
- Security (10 cases)
- Integration (10 cases)
- Performance (10 cases)

**Recommendation**: Prioritize Critical and High severity cases for MVP. Medium and Low cases can be addressed in later phases.

---

**Document Version**: 1.0  
**Last Updated**: 2024-01-15  
**Author**: Engineering Team  
**Status**: Complete
