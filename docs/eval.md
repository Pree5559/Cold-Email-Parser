# Phase Evaluation Criteria: The Closer - Cold Email Writer + Send Bot

## Overview

This document provides comprehensive evaluation criteria for each phase of the Cold Email Writer + Send Bot implementation. Each phase includes task-level checklists, pass/fail criteria, testing requirements, and quality metrics to ensure successful completion.

**Purpose**: Provide clear, measurable criteria for evaluating AI-generated code and implementation quality.

---

## Phase 1: MVP Foundation Evaluation

### Phase Overview
**Objective**: Build a working prototype demonstrating core workflow
**Estimated Duration**: Week 1 (14.5 hours)
**Success Criteria**: Can generate 3+ personalized emails, preview before sending, send via SMTP, log to CSV

---

### Task 1.1: Project Setup

**Evaluation Checklist**:
- [ ] Project directory structure created as specified
- [ ] Python virtual environment initialized
- [ ] `requirements.txt` created with correct dependencies
- [ ] `.env.example` template created
- [ ] `README.md` created with setup instructions
- [ ] Dependencies install successfully (`pip install -r requirements.txt`)
- [ ] README includes clear setup steps
- [ ] README includes usage instructions
- [ ] README includes troubleshooting section

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- Missing required files
- Dependencies fail to install
- README incomplete or unclear

**Quality Metrics**:
- Setup time < 5 minutes for new user
- Zero dependency conflicts
- README clarity score: 8/10 (user feedback)

**Automated Tests**:
```bash
# Test project structure
test -d the-closer
test -f requirements.txt
test -f .env.example
test -f README.md

# Test dependencies
pip install -r requirements.txt  # Should succeed without errors
```

---

### Task 1.2: Configuration Module

**Evaluation Checklist**:
- [ ] `config.py` module created
- [ ] Environment variables loaded using python-dotenv
- [ ] Configuration class defined with all required fields
- [ ] Validation for required config values implemented
- [ ] Dry-run mode flag implemented
- [ ] Default values for optional config
- [ ] Clear error messages for missing config
- [ ] Type hints added to config fields
- [ ] Config can be imported and used by other modules

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- Config module missing or incomplete
- No validation for required fields
- Dry-run mode not implemented

**Quality Metrics**:
- Config loading time < 100ms
- All config fields have type hints
- Error messages are clear and actionable

**Automated Tests**:
```python
# Test config loading
def test_config_loads():
    config = Config()
    assert config.SMTP_HOST is not None
    assert config.DRY_RUN in [True, False]

# Test validation
def test_config_validation():
    # Test with missing required env var
    # Should raise clear error
    pass

# Test dry-run mode
def test_dry_run_mode():
    config = Config()
    assert hasattr(config, 'DRY_RUN')
```

---

### Task 1.3: Input Loader Module (Hardcoded Data)

**Evaluation Checklist**:
- [ ] `input_loader.py` module created
- [ ] Contact data schema defined
- [ ] Hardcoded sample data includes 3-5 contacts
- [ ] Basic validation for required fields implemented
- [ ] Data normalization function implemented
- [ ] Each sample contact has all required fields
- [ ] Sample contacts have diverse data (different companies, roles)
- [ ] Validation errors are clear and specific
- [ ] Module can be imported independently

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- Input loader missing
- No validation for required fields
- Sample data incomplete or invalid

**Quality Metrics**:
- Validation accuracy: 100% for required fields
- Error message specificity: includes field name and issue
- Data normalization handles edge cases (whitespace, etc.)

**Automated Tests**:
```python
# Test data loading
def test_load_hardcoded_data():
    loader = InputLoader()
    contacts = loader.load_from_list(SAMPLE_CONTACTS)
    assert len(contacts) >= 3
    assert all('recipient_email' in c for c in contacts)

# Test validation
def test_validate_record():
    loader = InputLoader()
    # Test valid record
    assert loader.validate_record(valid_record) == True
    # Test missing required field
    assert loader.validate_record(invalid_record) == False

# Test normalization
def test_normalize_data():
    loader = InputLoader()
    normalized = loader.normalize_record({"name": "  John  "})
    assert normalized["name"] == "John"
```

---

### Task 1.4: Email Generator Module

**Evaluation Checklist**:
- [ ] `email_generator.py` module created
- [ ] Email template structure defined
- [ ] Subject line generation implemented
- [ ] Body generation implemented with f-string templates
- [ ] Word count validation implemented (<150 words)
- [ ] Email completeness validation implemented
- [ ] Template uses all personalization variables
- [ ] Generated emails follow required structure
- [ ] Module handles missing optional fields gracefully

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- Email generator missing
- Template doesn't use personalization variables
- No word count validation

**Quality Metrics**:
- Email generation time < 50ms per email
- Word count accuracy: ±5 words
- Template completeness: uses all available variables

**Automated Tests**:
```python
# Test email generation
def test_generate_email():
    generator = EmailGenerator()
    email = generator.generate_email(sample_record)
    assert 'subject' in email
    assert 'body' in email
    assert len(email['body'].split()) < 150

# Test word count
def test_word_count_validation():
    generator = EmailGenerator()
    email = generator.generate_email(sample_record)
    word_count = generator.count_words(email['body'])
    assert word_count < 150

# Test template uses variables
def test_template_variables():
    generator = EmailGenerator()
    email = generator.generate_email(sample_record)
    assert sample_record['company'] in email['body']
    assert sample_record['role'] in email['body']
```

---

### Task 1.5: Preview Handler Module

**Evaluation Checklist**:
- [ ] `preview_handler.py` module created
- [ ] Formatted email display implemented
- [ ] Confirmation prompt (yes/no/skip) implemented
- [ ] Preview formatting has clear sections
- [ ] User input validation implemented
- [ ] Preview shows all key fields (to, company, role, subject, body)
- [ ] Preview handles special characters correctly
- [ ] Invalid input reprompts correctly
- [ ] Preview is readable in terminal

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- Preview handler missing
- No confirmation prompt
- Preview doesn't show key fields

**Quality Metrics**:
- Preview rendering time < 100ms
- Input validation catches all invalid inputs
- Preview formatting is clear and readable

**Automated Tests**:
```python
# Test preview formatting
def test_preview_formatting():
    handler = PreviewHandler()
    preview = handler.format_preview(email, record)
    assert 'To:' in preview
    assert 'Subject:' in preview
    assert '────────' in preview  # Separator

# Test confirmation
def test_get_confirmation():
    handler = PreviewHandler()
    # Mock user input
    result = handler.get_confirmation()
    assert result in ['yes', 'no', 'skip']

# Test input validation
def test_invalid_input_reprompt():
    handler = PreviewHandler()
    # Test with invalid input
    # Should reprompt
    pass
```

---

### Task 1.6: Email Sender Module (SMTP)

**Evaluation Checklist**:
- [ ] `email_sender.py` module created
- [ ] SMTP connection logic implemented
- [ ] Authentication with credentials implemented
- [ ] `send_email` function implemented
- [ ] Dry-run mode support implemented
- [ ] Error handling and retry logic implemented
- [ ] Connection cleanup implemented
- [ ] Handles SMTP errors gracefully
- [ ] Logs send attempts

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- Email sender missing
- No SMTP connection logic
- No dry-run mode support

**Quality Metrics**:
- Connection time < 5 seconds
- Send time < 10 seconds per email
- Error handling covers common SMTP errors

**Automated Tests**:
```python
# Test dry-run mode
def test_dry_run_mode():
    config = Config(DRY_RUN=True)
    sender = EmailSender(config)
    result = sender.send_email(to, subject, body)
    assert result == True  # Should succeed in dry-run
    # Verify no actual email sent

# Test SMTP connection
def test_smtp_connection():
    config = Config(DRY_RUN=False)
    sender = EmailSender(config)
    sender.connect()
    assert sender.smtp is not None
    sender.disconnect()

# Test error handling
def test_send_error_handling():
    # Test with invalid credentials
    # Should handle error gracefully
    pass
```

---

### Task 1.7: Logger Module

**Evaluation Checklist**:
- [ ] `logger.py` module created
- [ ] Log entry schema defined
- [ ] CSV file creation with headers implemented
- [ ] Log entry function implemented
- [ ] Timestamp generation implemented
- [ ] Error message logging implemented
- [ ] Log file created if doesn't exist
- [ ] Log entries append correctly
- [ ] CSV format is valid

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- Logger module missing
- No CSV file creation
- Log entries don't append correctly

**Quality Metrics**:
- Log write time < 50ms per entry
- CSV format is valid (can be read by pandas/Excel)
- Timestamps are in ISO 8601 format

**Automated Tests**:
```python
# Test log file creation
def test_log_file_creation():
    logger = Logger('test_log.csv')
    logger.log_entry(record, email, 'sent')
    assert os.path.exists('test_log.csv')

# Test log entry format
def test_log_entry_format():
    logger = Logger('test_log.csv')
    logger.log_entry(record, email, 'sent')
    # Read and validate CSV format
    df = pd.read_csv('test_log.csv')
    assert 'timestamp' in df.columns
    assert 'status' in df.columns

# Test timestamp format
def test_timestamp_format():
    logger = Logger('test_log.csv')
    logger.log_entry(record, email, 'sent')
    df = pd.read_csv('test_log.csv')
    # Validate ISO 8601 format
    pass
```

---

### Task 1.8: Main Orchestration Script

**Evaluation Checklist**:
- [ ] `main.py` script created
- [ ] All modules imported correctly
- [ ] Main workflow loop implemented
- [ ] Error handling at orchestration level
- [ ] Graceful shutdown implemented
- [ ] Progress indicators added
- [ ] Workflow follows: load → generate → preview → send → log
- [ ] Handles each contact sequentially
- [ ] Shows summary at end

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- Main script missing or incomplete
- Workflow doesn't follow required sequence
- No error handling

**Quality Metrics**:
- End-to-end execution time < 30 seconds for 5 contacts
- Progress indicators are clear
- Error handling prevents crashes

**Automated Tests**:
```bash
# Test main script runs
python main.py --dry-run
# Should complete without errors

# Test with sample data
python main.py
# Should process all contacts
```

---

### Task 1.9: Testing & Debugging

**Evaluation Checklist**:
- [ ] Tested with dry-run mode enabled
- [ ] Verified email generation for all contacts
- [ ] Tested preview functionality
- [ ] Tested skip functionality
- [ ] Tested error handling (invalid email, etc.)
- [ ] Verified log file creation
- [ ] Sent test email to self (dry-run disabled)
- [ ] Verified email in sent folder
- [ ] Documented any bugs found
- [ ] All bugs fixed

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- Critical bugs remaining
- Test email not verified in sent folder
- Log file not created

**Quality Metrics**:
- Zero critical bugs
- All test scenarios pass
- Email appears in sent folder within 1 minute

**Manual Test Procedure**:
```bash
# 1. Enable dry-run
DRY_RUN=true python main.py

# 2. Verify all emails generated
# 3. Test preview (enter 'skip' for all)
# 4. Test with invalid email in contacts
# 5. Disable dry-run
DRY_RUN=false python main.py
# 6. Send one test email to self
# 7. Check sent folder
# 8. Verify log file
```

---

### Task 1.10: Documentation

**Evaluation Checklist**:
- [ ] README.md updated with setup instructions
- [ ] Gmail App Password setup guide added
- [ ] Environment variables documented
- [ ] Usage examples added
- [ ] Troubleshooting steps documented
- [ ] Prerequisites listed
- [ ] Quick start guide included
- [ ] Screenshots or examples (optional)
- [ ] Contact information for support (optional)

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- README incomplete
- No setup instructions
- No troubleshooting section

**Quality Metrics**:
- Setup time following README < 10 minutes
- README clarity score: 8/10 (user feedback)
- Covers common issues

---

### Phase 1 Overall Evaluation

**Phase Completion Criteria**:
- [ ] All 10 tasks completed
- [ ] All task-level checklists passed
- [ ] End-to-end test successful
- [ ] Zero critical bugs
- [ ] Documentation complete

**Phase Pass Score**: 90% (9/10 tasks must pass)

**Phase Fail Criteria**:
- More than 1 task fails
- Critical bug in core workflow
- Cannot send emails end-to-end

**Quality Gates**:
- Code review passed
- All automated tests pass
- Manual testing successful
- Documentation approved

**Sign-off Requirements**:
- Demo of working MVP
- Test email sent and verified
- Log file reviewed
- README reviewed

---

## Phase 2: Enhanced Input & Validation Evaluation

### Phase Overview
**Objective**: Add file-based input support (JSON/CSV) and robust validation
**Estimated Duration**: Week 2 (10.5 hours)
**Success Criteria**: Can load from JSON/CSV, comprehensive validation, clear error messages

---

### Task 2.1: JSON File Loading

**Evaluation Checklist**:
- [ ] JSON loading function added to input_loader.py
- [ ] JSON file parsing implemented
- [ ] JSON schema validation implemented
- [ ] File not found error handling
- [ ] JSON format documentation added
- [ ] `contacts.json` example file created
- [ ] Handles malformed JSON gracefully
- [ ] Validates JSON structure
- [ ] Error messages include line numbers

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- JSON loading not implemented
- No error handling for malformed JSON
- No example file

**Quality Metrics**:
- JSON parsing time < 100ms for 100 contacts
- Error messages are specific (include line number)
- Schema validation catches all structural errors

**Automated Tests**:
```python
# Test JSON loading
def test_load_from_json():
    loader = InputLoader()
    contacts = loader.load_from_json('contacts.json')
    assert len(contacts) > 0
    assert all('recipient_email' in c for c in contacts)

# Test malformed JSON
def test_malformed_json():
    loader = InputLoader()
    with pytest.raises(JSONParseError):
        loader.load_from_json('malformed.json')

# Test file not found
def test_file_not_found():
    loader = InputLoader()
    with pytest.raises(FileNotFoundError):
        loader.load_from_json('nonexistent.json')
```

---

### Task 2.2: CSV File Loading

**Evaluation Checklist**:
- [ ] CSV loading function added to input_loader.py
- [ ] CSV file parsing implemented
- [ ] CSV column mapping to schema implemented
- [ ] Handles missing columns gracefully
- [ ] CSV format documentation added
- [ ] `jobs.csv` example file created
- [ ] Handles malformed CSV rows
- [ ] Validates CSV structure
- [ ] Error messages include row numbers

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- CSV loading not implemented
- No column mapping
- No example file

**Quality Metrics**:
- CSV parsing time < 100ms for 100 contacts
- Handles missing columns without crashing
- Error messages include row number

**Automated Tests**:
```python
# Test CSV loading
def test_load_from_csv():
    loader = InputLoader()
    contacts = loader.load_from_csv('jobs.csv')
    assert len(contacts) > 0

# Test missing columns
def test_missing_columns():
    loader = InputLoader()
    # Should handle gracefully
    contacts = loader.load_from_csv('incomplete.csv')
    # Should use defaults or skip

# Test malformed rows
def test_malformed_rows():
    loader = InputLoader()
    # Should skip bad rows, log errors
    contacts = loader.load_from_csv('malformed.csv')
```

---

### Task 2.3: Enhanced Validation

**Evaluation Checklist**:
- [ ] Validation error class created
- [ ] Email format validation (regex) implemented
- [ ] URL format validation implemented
- [ ] Required field checking implemented
- [ ] Field type validation implemented
- [ ] Detailed error messages implemented
- [ ] Validation rules documented
- [ ] All field types validated
- [ ] Error messages are actionable

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- No validation error class
- Email format not validated
- Error messages not detailed

**Quality Metrics**:
- Validation accuracy: 100% for required fields
- Email regex catches all invalid formats
- Error messages specify field and issue

**Automated Tests**:
```python
# Test email validation
def test_email_validation():
    validator = Validator()
    assert validator.validate_email('valid@example.com') == True
    assert validator.validate_email('invalid') == False
    assert validator.validate_email('@example.com') == False

# Test URL validation
def test_url_validation():
    validator = Validator()
    assert validator.validate_url('https://example.com') == True
    assert validator.validate_url('not-a-url') == False

# Test required fields
def test_required_fields():
    validator = Validator()
    record = {'recipient_email': 'test@example.com'}  # Missing required
    errors = validator.validate(record)
    assert len(errors) > 0
```

---

### Task 2.4: Input Source Selection

**Evaluation Checklist**:
- [ ] argparse added to main.py
- [ ] Input source detection implemented
- [ ] Fallback to hardcoded data
- [ ] Usage with different inputs documented
- [ ] Help message implemented
- [ ] Invalid input source handled
- [ ] CLI arguments validated
- [ ] Default behavior documented

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- No CLI argument parsing
- No fallback to hardcoded data
- No documentation

**Quality Metrics**:
- CLI responds to --help
- All input sources work correctly
- Error messages for invalid inputs

**Automated Tests**:
```bash
# Test JSON input
python main.py --input contacts.json

# Test CSV input
python main.py --input jobs.csv

# Test default (hardcoded)
python main.py

# Test help
python main.py --help

# Test invalid input
python main.py --input nonexistent.json
```

---

### Task 2.5: Data Normalization

**Evaluation Checklist**:
- [ ] Field name mapping implemented
- [ ] Handles different CSV column names
- [ ] Trims whitespace from fields
- [ ] Converts empty strings to None
- [ ] Default values for optional fields
- [ ] Normalization logic documented
- [ ] Handles special characters
- [ ] Preserves valid data
- [ ] Logs normalization actions

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- No normalization implemented
- Whitespace not trimmed
- No default values

**Quality Metrics**:
- Normalization handles all edge cases
- Preserves valid data
- Logs normalization actions

**Automated Tests**:
```python
# Test whitespace trimming
def test_trim_whitespace():
    normalizer = Normalizer()
    result = normalizer.normalize({'name': '  John  '})
    assert result['name'] == 'John'

# Test empty string to None
def test_empty_string_to_none():
    normalizer = Normalizer()
    result = normalizer.normalize({'company': ''})
    assert result['company'] is None

# Test field mapping
def test_field_mapping():
    normalizer = Normalizer()
    result = normalizer.normalize({'Email': 'test@example.com'})
    assert result['recipient_email'] == 'test@example.com'
```

---

### Task 2.6: Testing File Inputs

**Evaluation Checklist**:
- [ ] Test JSON file with valid data created
- [ ] Test CSV file with valid data created
- [ ] Test files with invalid data created
- [ ] Error handling for invalid files tested
- [ ] Missing file handling tested
- [ ] Data normalization tested
- [ ] All input formats tested
- [ ] Test results documented
- [ ] Edge cases covered

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- Test files not created
- Invalid file handling not tested
- Edge cases not covered

**Quality Metrics**:
- All test scenarios pass
- Edge cases handled correctly
- Test documentation complete

**Manual Test Procedure**:
```bash
# Test valid JSON
python main.py --input test_valid.json

# Test valid CSV
python main.py --input test_valid.csv

# Test invalid JSON
python main.py --input test_invalid.json

# Test invalid CSV
python main.py --input test_invalid.csv

# Test missing file
python main.py --input nonexistent.json

# Verify all error messages are clear
```

---

### Phase 2 Overall Evaluation

**Phase Completion Criteria**:
- [ ] All 6 tasks completed
- [ ] All task-level checklists passed
- [ ] JSON loading works
- [ ] CSV loading works
- [ ] Validation enhanced
- [ ] Input source selection works

**Phase Pass Score**: 85% (5/6 tasks must pass)

**Phase Fail Criteria**:
- More than 1 task fails
- Cannot load from JSON or CSV
- Validation not enhanced

**Quality Gates**:
- All input formats tested
- Validation covers all fields
- Error messages are clear

**Sign-off Requirements**:
- Demo of JSON loading
- Demo of CSV loading
- Validation tested with invalid data
- Documentation reviewed

---

## Phase 3: Advanced Features Evaluation

### Phase Overview
**Objective**: Add Gmail draft mode, multiple templates, and LLM integration options
**Estimated Duration**: Week 3 (16 hours)
**Success Criteria**: Gmail drafts work, multiple templates available, optional LLM integration

---

### Task 3.1: Gmail API Integration

**Evaluation Checklist**:
- [ ] google-api-python-client added to requirements
- [ ] OAuth2 authentication flow implemented
- [ ] Gmail service client created
- [ ] Draft creation function implemented
- [ ] Draft mode configuration option added
- [ ] Gmail API errors handled
- [ ] OAuth setup documentation added
- [ ] Updated configuration for Gmail
- [ ] Token refresh implemented

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- Gmail API integration not implemented
- No OAuth flow
- No draft creation

**Quality Metrics**:
- OAuth flow completes successfully
- Draft creation works
- Token refresh works automatically

**Automated Tests**:
```python
# Test OAuth flow
def test_oauth_flow():
    gmail = GmailSender(credentials)
    assert gmail.authenticate() == True

# Test draft creation
def test_create_draft():
    gmail = GmailSender(credentials)
    draft = gmail.create_draft(to, subject, body)
    assert 'id' in draft

# Test token refresh
def test_token_refresh():
    # Test with expired token
    # Should refresh automatically
    pass
```

---

### Task 3.2: Multiple Email Templates

**Evaluation Checklist**:
- [ ] Templates directory created
- [ ] 3-5 email templates designed
- [ ] Template selection logic implemented
- [ ] Template configuration added
- [ ] Template documentation created
- [ ] Each template follows email structure
- [ ] Templates use personalization variables
- [ ] Word count validation for each template
- [ ] User can select template

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- No template directory
- Less than 3 templates
- No template selection logic

**Quality Metrics**:
- All templates follow structure
- All templates < 150 words
- Template selection works

**Automated Tests**:
```python
# Test template loading
def test_load_templates():
    generator = EmailGenerator()
    templates = generator.load_templates()
    assert len(templates) >= 3

# Test template selection
def test_template_selection():
    generator = EmailGenerator()
    email = generator.generate_email(record, template='direct')
    assert email is not None

# Test all templates
def test_all_templates():
    generator = EmailGenerator()
    for template in generator.templates:
        email = generator.generate_email(record, template)
        assert len(email['body'].split()) < 150
```

---

### Task 3.3: LLM Integration (Optional)

**Evaluation Checklist**:
- [ ] Groq API client added to requirements
- [ ] Email rewriting function implemented
- [ ] Tone adjustment options implemented
- [ ] API error handling implemented
- [ ] LLM configuration added
- [ ] Fallback to template if LLM fails
- [ ] LLM usage documented
- [ ] API key validation
- [ ] Cost tracking implemented

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- LLM integration not implemented (optional)
- No fallback if LLM fails
- No error handling

**Quality Metrics**:
- LLM generates valid emails
- Fallback works when LLM fails
- Cost tracking accurate

**Automated Tests**:
```python
# Test LLM integration
def test_llm_enhance():
    enhancer = LLMEmailEnhancer(api_key)
    enhanced = enhancer.enhance_email(subject, body)
    assert enhanced is not None

# Test fallback
def test_fallback():
    enhancer = LLMEmailEnhancer(invalid_key)
    # Should fallback to template
    email = enhancer.enhance_or_fallback(subject, body)
    assert email is not None

# Test tone adjustment
def test_tone_adjustment():
    enhancer = LLMEmailEnhancer(api_key)
    casual = enhancer.enhance_email(subject, body, tone='casual')
    professional = enhancer.enhance_email(subject, body, tone='professional')
    assert casual != professional
```

---

### Task 3.4: Email Quality Scoring

**Evaluation Checklist**:
- [ ] Quality criteria defined
- [ ] Scoring algorithm implemented
- [ ] Word count check implemented
- [ ] Personalization check implemented
- [ ] Clarity check implemented
- [ ] Score display in preview implemented
- [ ] Scoring criteria documented
- [ ] Score thresholds defined
- [ ] Quality suggestions provided

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- No quality scoring
- Score not displayed in preview
- No quality criteria

**Quality Metrics**:
- Scoring algorithm accurate
- Score displayed clearly
- Suggestions are helpful

**Automated Tests**:
```python
# Test quality scoring
def test_quality_score():
    scorer = QualityScorer()
    score = scorer.score_email(email)
    assert 0 <= score <= 100

# Test word count check
def test_word_count_check():
    scorer = QualityScorer()
    result = scorer.check_word_count(email)
    assert result['pass'] == (len(email['body'].split()) < 150)

# Test personalization check
def test_personalization_check():
    scorer = QualityScorer()
    result = scorer.check_personalization(email, record)
    assert result['has_personalization'] == True
```

---

### Task 3.5: Subject Line Variations

**Evaluation Checklist**:
- [ ] Subject line templates created
- [ ] Subject generation implemented
- [ ] Subject selection in preview implemented
- [ ] A/B testing framework (basic) implemented
- [ ] Multiple subject options generated
- [ ] Subject selection UI added
- [ ] Subject templates documented
- [ ] Subject length validation
- [ ] Subject relevance check

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- No subject variations
- No subject selection
- Only one subject template

**Quality Metrics**:
- Multiple subjects generated
- Subjects are relevant
- Selection works in preview

**Automated Tests**:
```python
# Test subject generation
def test_subject_generation():
    generator = EmailGenerator()
    subjects = generator.generate_subjects(record)
    assert len(subjects) >= 3

# Test subject selection
def test_subject_selection():
    generator = EmailGenerator()
    subjects = generator.generate_subjects(record)
    selected = generator.select_subject(subjects)
    assert selected in subjects
```

---

### Task 3.6: Spam Risk Checker

**Evaluation Checklist**:
- [ ] Spam trigger words defined
- [ ] Spam word detection implemented
- [ ] Capitalization check implemented
- [ ] Exclamation mark check implemented
- [ ] Spam risk display in preview implemented
- [ ] Spam word list documented
- [ ] Risk thresholds defined
- [ ] Spam suggestions provided
- [ ] False positive handling

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- No spam checker
- No risk display
- No spam word list

**Quality Metrics**:
- Spam detection accurate
- Risk display clear
- Low false positive rate

**Automated Tests**:
```python
# Test spam detection
def test_spam_detection():
    checker = SpamChecker()
    spam_email = "FREE MONEY!!! Click now!!!"
    risk = checker.check_risk(spam_email)
    assert risk > 0.5

# Test capitalization check
def test_capitalization_check():
    checker = SpamChecker()
    all_caps = "THIS IS ALL CAPS"
    risk = checker.check_capitalization(all_caps)
    assert risk > 0

# Test exclamation check
def test_exclamation_check():
    checker = SpamChecker()
    many_excl = "Hello!!! How are you???"
    risk = checker.check_exclamation(many_excl)
    assert risk > 0
```

---

### Phase 3 Overall Evaluation

**Phase Completion Criteria**:
- [ ] All 6 tasks completed (LLM optional)
- [ ] All task-level checklists passed
- [ ] Gmail draft mode works
- [ ] Multiple templates available
- [ ] Quality scoring works
- [ ] Subject variations work
- [ ] Spam checker works

**Phase Pass Score**: 80% (5/6 tasks must pass, LLM optional)

**Phase Fail Criteria**:
- More than 2 tasks fail
- Gmail draft mode doesn't work
- No multiple templates

**Quality Gates**:
- Gmail API tested
- All templates tested
- Quality metrics validated

**Sign-off Requirements**:
- Demo of Gmail draft creation
- Demo of template selection
- Quality scoring reviewed
- Spam checker tested

---

## Phase 4: Production Readiness Evaluation

### Phase Overview
**Objective**: Add web UI, database backend, user authentication, and analytics
**Estimated Duration**: Week 4 (35 hours)
**Success Criteria**: Web UI functional, database works, authentication secure, analytics display

---

### Task 4.1: Streamlit Web UI

**Evaluation Checklist**:
- [ ] Streamlit added to requirements
- [ ] UI layout designed
- [ ] Contact upload (CSV/JSON) implemented
- [ ] Email preview in web implemented
- [ ] Send/draft buttons implemented
- [ ] Progress display implemented
- [ ] UI responsive design
- [ ] Error handling in UI
- [ ] UI documentation created

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- Streamlit UI not created
- No contact upload
- No email preview

**Quality Metrics**:
- UI loads in < 3 seconds
- All UI elements functional
- Responsive design works

**Automated Tests**:
```bash
# Test Streamlit app starts
streamlit run app.py

# Test UI loads
# Manual testing of all UI elements
```

---

### Task 4.2: Database Integration

**Evaluation Checklist**:
- [ ] Database schema designed
- [ ] SQLite connection implemented
- [ ] Contacts table created
- [ ] Logs table created
- [ ] CRUD operations implemented
- [ ] Database migration logic implemented
- [ ] Database documentation created
- [ ] Backup/restore implemented
- [ ] Query optimization

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- No database integration
- No CRUD operations
- No migration logic

**Quality Metrics**:
- Database queries < 100ms
- CRUD operations work correctly
- Migration logic safe

**Automated Tests**:
```python
# Test database connection
def test_db_connection():
    db = Database()
    assert db.connect() == True

# Test CRUD operations
def test_crud():
    db = Database()
    # Create
    db.create_contact(contact)
    # Read
    retrieved = db.get_contact(contact_id)
    assert retrieved is not None
    # Update
    db.update_contact(contact_id, updates)
    # Delete
    db.delete_contact(contact_id)
```

---

### Task 4.3: User Authentication

**Evaluation Checklist**:
- [ ] User table schema designed
- [ ] Password hashing implemented
- [ ] Login/logout functionality implemented
- [ ] Session management implemented
- [ ] Authentication decorators added
- [ ] User registration implemented
- [ ] Password requirements enforced
- [ ] Session timeout implemented
- [ ] Security documentation created

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- No authentication
- No password hashing
- No session management

**Quality Metrics**:
- Passwords hashed correctly
- Sessions secure
- Login/logout works

**Automated Tests**:
```python
# Test password hashing
def test_password_hashing():
    auth = Auth()
    hashed = auth.hash_password('password123')
    assert auth.verify_password('password123', hashed) == True
    assert auth.verify_password('wrong', hashed) == False

# Test login
def test_login():
    auth = Auth()
    user = auth.login('username', 'password')
    assert user is not None

# Test session management
def test_session():
    auth = Auth()
    session = auth.create_session(user_id)
    assert auth.validate_session(session) == True
```

---

### Task 4.4: Analytics Dashboard

**Evaluation Checklist**:
- [ ] Analytics metrics defined
- [ ] Statistics calculation implemented
- [ ] Dashboard UI created
- [ ] Charts and graphs added
- [ ] Date range filtering implemented
- [ ] Export functionality implemented
- [ ] Real-time updates
- [ ] Performance optimization
- [ ] Dashboard documentation created

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- No analytics dashboard
- No statistics calculation
- No charts/graphs

**Quality Metrics**:
- Dashboard loads in < 2 seconds
- Statistics accurate
- Charts render correctly

**Automated Tests**:
```python
# Test statistics calculation
def test_statistics():
    analytics = Analytics()
    stats = analytics.calculate_stats()
    assert 'total_sent' in stats
    assert 'success_rate' in stats

# Test date range filtering
def test_date_filter():
    analytics = Analytics()
    stats = analytics.calculate_stats(start_date, end_date)
    assert stats is not None
```

---

### Task 4.5: API Endpoints

**Evaluation Checklist**:
- [ ] API endpoints designed
- [ ] Flask/FastAPI application implemented
- [ ] Authentication middleware added
- [ ] Contact CRUD endpoints implemented
- [ ] Email generation endpoint implemented
- [ ] API documentation created
- [ ] Endpoint testing implemented
- [ ] Rate limiting implemented
- [ ] API versioning

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- No API endpoints
- No authentication middleware
- No API documentation

**Quality Metrics**:
- API response time < 200ms
- All endpoints functional
- Documentation complete

**Automated Tests**:
```python
# Test API endpoints
def test_get_contacts():
    response = client.get('/api/contacts')
    assert response.status_code == 200

def test_create_contact():
    response = client.post('/api/contacts', json=contact)
    assert response.status_code == 201

def test_auth_required():
    response = client.get('/api/contacts')
    assert response.status_code == 401  # Unauthorized
```

---

### Task 4.6: Deployment Configuration

**Evaluation Checklist**:
- [ ] Dockerfile created
- [ ] docker-compose.yml created
- [ ] Production environment config created
- [ ] Health checks implemented
- [ ] Logging configuration added
- [ ] Deployment documentation created
- [ ] Environment variables documented
- [ ] Security hardening
- [ ] Backup strategy

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- No Docker configuration
- No deployment documentation
- No health checks

**Quality Metrics**:
- Docker image builds successfully
- Health checks pass
- Deployment documented

**Automated Tests**:
```bash
# Test Docker build
docker build -t closer-app .

# Test Docker compose
docker-compose up -d

# Test health check
curl http://localhost:8000/health
```

---

### Task 4.7: Testing & QA

**Evaluation Checklist**:
- [ ] Unit tests for new features written
- [ ] Integration tests written
- [ ] End-to-end testing performed
- [ ] Security audit completed
- [ ] Performance testing completed
- [ ] User acceptance testing completed
- [ ] Test coverage > 80%
- [ ] All tests passing
- [ ] Test documentation created

**Pass Criteria**: All checklist items completed

**Fail Criteria**:
- Test coverage < 80%
- Critical bugs found
- Security vulnerabilities

**Quality Metrics**:
- Test coverage > 80%
- All tests passing
- Zero critical vulnerabilities

**Automated Tests**:
```bash
# Run all tests
pytest --cov=. --cov-report=html

# Check coverage
coverage report

# Security audit
bandit -r .

# Performance test
locust -f locustfile.py
```

---

### Phase 4 Overall Evaluation

**Phase Completion Criteria**:
- [ ] All 7 tasks completed
- [ ] All task-level checklists passed
- [ ] Web UI functional
- [ ] Database integration works
- [ ] Authentication secure
- [ ] Analytics display correctly
- [ ] API endpoints functional
- [ ] Can be deployed via Docker
- [ ] All tests passing

**Phase Pass Score**: 85% (6/7 tasks must pass)

**Phase Fail Criteria**:
- More than 1 task fails
- Web UI not functional
- Authentication not secure
- Tests not passing

**Quality Gates**:
- Security audit passed
- Performance tests passed
- Test coverage > 80%
- User acceptance passed

**Sign-off Requirements**:
- Demo of web UI
- Security audit reviewed
- Performance metrics reviewed
- Deployment tested

---

## Overall Project Evaluation

### Final Completion Criteria

**All Phases Complete**:
- [ ] Phase 1: MVP Foundation - Complete
- [ ] Phase 2: Enhanced Input & Validation - Complete
- [ ] Phase 3: Advanced Features - Complete
- [ ] Phase 4: Production Readiness - Complete

**Overall Quality Gates**:
- [ ] All automated tests passing
- [ ] Manual testing successful
- [ ] Code review approved
- [ ] Security audit passed
- [ ] Documentation complete
- [ ] Demo successful

**Project Pass Score**: 85% overall (all phases must meet minimum pass scores)

### Final Deliverables Checklist

**Code**:
- [ ] All source code committed
- [ ] No critical bugs
- [ ] Code follows style guidelines
- [ ] Comments where needed

**Documentation**:
- [ ] README complete
- [ ] API documentation complete
- [ ] Architecture document complete
- [ ] Deployment guide complete

**Testing**:
- [ ] Unit tests written
- [ ] Integration tests written
- [ ] Test coverage > 80%
- [ ] All tests passing

**Security**:
- [ ] No hardcoded credentials
- [ ] Security audit passed
- [ ] Dependencies up to date
- [ ] Vulnerabilities addressed

### Evaluation Scoring Rubric

**Phase Scoring**:
- 90-100%: Excellent - Exceeds expectations
- 80-89%: Good - Meets expectations
- 70-79%: Acceptable - Minor issues
- 60-69%: Needs Improvement - Significant issues
- < 60%: Fail - Major issues

**Task Scoring**:
- 100%: All checklist items complete
- 75%: Most items complete, minor gaps
- 50%: Half items complete
- 25%: Few items complete
- 0%: Not started

**Quality Metrics Scoring**:
- Exceeds: All metrics met or exceeded
- Meets: All metrics met
- Partially Meets: Some metrics met
- Does Not Meet: Most metrics not met

### Evaluation Process

**Step 1: Task-Level Evaluation**
- Review each task checklist
- Verify automated tests pass
- Check code quality
- Document findings

**Step 2: Phase-Level Evaluation**
- Aggregate task scores
- Verify phase completion criteria
- Check quality gates
- Document phase results

**Step 3: Project-Level Evaluation**
- Aggregate phase scores
- Verify final completion criteria
- Review overall quality gates
- Document project results

**Step 4: Sign-Off**
- Review all findings
- Address any blockers
- Obtain approval
- Document sign-off

### Continuous Evaluation

**During Development**:
- Run automated tests after each task
- Review code before committing
- Update checklists as items complete
- Document issues as they arise

**After Each Phase**:
- Run full test suite
- Review phase completion
- Document lessons learned
- Plan next phase

**Final Review**:
- Comprehensive testing
- Security audit
- Performance review
- User acceptance testing

---

## Automated Evaluation Script

### Phase 1 Evaluation Script

```bash
#!/bin/bash
# Phase 1 Automated Evaluation

echo "=== Phase 1 Evaluation ==="

# Check project structure
echo "Checking project structure..."
test -f requirements.txt && echo "✓ requirements.txt exists" || echo "✗ requirements.txt missing"
test -f .env.example && echo "✓ .env.example exists" || echo "✗ .env.example missing"
test -f README.md && echo "✓ README.md exists" || echo "✗ README.md missing"
test -f config.py && echo "✓ config.py exists" || echo "✗ config.py missing"
test -f input_loader.py && echo "✓ input_loader.py exists" || echo "✗ input_loader.py missing"
test -f email_generator.py && echo "✓ email_generator.py exists" || echo "✗ email_generator.py missing"
test -f preview_handler.py && echo "✓ preview_handler.py exists" || echo "✗ preview_handler.py missing"
test -f email_sender.py && echo "✓ email_sender.py exists" || echo "✗ email_sender.py missing"
test -f logger.py && echo "✓ logger.py exists" || echo "✗ logger.py missing"
test -f main.py && echo "✓ main.py exists" || echo "✗ main.py missing"

# Run tests
echo "Running tests..."
python -m pytest tests/ -v

# Check dependencies
echo "Checking dependencies..."
pip install -r requirements.txt

# Test dry-run
echo "Testing dry-run mode..."
DRY_RUN=true python main.py

echo "=== Phase 1 Evaluation Complete ==="
```

### Phase 2 Evaluation Script

```bash
#!/bin/bash
# Phase 2 Automated Evaluation

echo "=== Phase 2 Evaluation ==="

# Check JSON loading
echo "Testing JSON loading..."
python main.py --input contacts.json

# Check CSV loading
echo "Testing CSV loading..."
python main.py --input jobs.csv

# Test validation
echo "Testing validation..."
python -c "from input_loader import InputLoader; loader = InputLoader(); print('Validation OK')"

# Test normalization
echo "Testing normalization..."
python -c "from input_loader import InputLoader; loader = InputLoader(); print('Normalization OK')"

echo "=== Phase 2 Evaluation Complete ==="
```

### Phase 3 Evaluation Script

```bash
#!/bin/bash
# Phase 3 Automated Evaluation

echo "=== Phase 3 Evaluation ==="

# Check Gmail integration
echo "Testing Gmail integration..."
python -c "from email_sender import GmailSender; print('Gmail OK')"

# Test templates
echo "Testing templates..."
python -c "from email_generator import EmailGenerator; gen = EmailGenerator(); print(f'Templates: {len(gen.templates)}')"

# Test quality scoring
echo "Testing quality scoring..."
python -c "from quality_scorer import QualityScorer; scorer = QualityScorer(); print('Quality scorer OK')"

# Test spam checker
echo "Testing spam checker..."
python -c "from spam_checker import SpamChecker; checker = SpamChecker(); print('Spam checker OK')"

echo "=== Phase 3 Evaluation Complete ==="
```

### Phase 4 Evaluation Script

```bash
#!/bin/bash
# Phase 4 Automated Evaluation

echo "=== Phase 4 Evaluation ==="

# Test Streamlit
echo "Testing Streamlit app..."
streamlit run app.py &

# Test database
echo "Testing database..."
python -c "from database import Database; db = Database(); print('Database OK')"

# Test authentication
echo "Testing authentication..."
python -c "from auth import Auth; auth = Auth(); print('Auth OK')"

# Test API
echo "Testing API..."
curl http://localhost:8000/api/health

# Run test suite
echo "Running full test suite..."
pytest --cov=. --cov-report=html

# Security audit
echo "Running security audit..."
bandit -r .

echo "=== Phase 4 Evaluation Complete ==="
```

---

## Evaluation Report Template

### Phase Evaluation Report

**Phase**: [Phase Name]
**Date**: [Date]
**Evaluator**: [Name]

**Task Results**:
| Task | Status | Score | Notes |
|------|--------|-------|-------|
| Task 1.1 | [Pass/Fail] | [0-100] | [Notes] |
| Task 1.2 | [Pass/Fail] | [0-100] | [Notes] |
| ... | ... | ... | ... |

**Phase Score**: [0-100]%

**Quality Metrics**:
- [Metric 1]: [Value/Status]
- [Metric 2]: [Value/Status]
- ...

**Issues Found**:
- [Issue 1]: [Severity]
- [Issue 2]: [Severity]
- ...

**Recommendations**:
- [Recommendation 1]
- [Recommendation 2]
- ...

**Sign-Off**: [Approved/Needs Revision/Rejected]

**Signature**: ________________

---

## Summary

This evaluation document provides comprehensive criteria for assessing each phase of the Cold Email Writer + Send Bot implementation. By following these checklists and quality metrics, you can ensure that each phase meets the required standards before proceeding to the next phase.

**Key Points**:
- Each task has a detailed checklist
- Pass/fail criteria are clearly defined
- Quality metrics provide objective measures
- Automated tests verify functionality
- Manual testing ensures user experience
- Sign-off requirements ensure accountability

**Next Steps**:
1. Use this document during development
2. Update checklists as tasks complete
3. Run automated tests regularly
4. Document issues as they arise
5. Review and sign off each phase

---

**Document Version**: 1.0  
**Last Updated**: 2024-01-15  
**Author**: Engineering Team  
**Status**: Ready for Use
