import sys
import argparse
from config import Config
from input_loader import InputLoader, ValidationError
from email_generator import EmailGenerator
from preview_handler import PreviewHandler
from email_sender import EmailSender
from logger import Logger


def main():
    """Main orchestration script for Phase 2 Enhanced Input."""
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="The Closer - Cold Email Writer + Send Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python phase1/main.py                    # Use hardcoded contacts
  python phase1/main.py --input contacts.json  # Load from JSON
  python phase1/main.py --input jobs.csv       # Load from CSV
"""
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Input file path (JSON or CSV). If not provided, uses hardcoded contacts."
    )
    args = parser.parse_args()
    
    print("=" * 60)
    print("THE CLOSER - Cold Email Writer + Send Bot")
    print("Phase 2: Enhanced Input & Validation")
    print("=" * 60)
    print()
    
    try:
        # Step 1: Load configuration
        print("Loading configuration...")
        config = Config()
        print(f"Configuration loaded: {config}")
        print()
        
        # Step 2: Load contacts
        print("Loading contacts...")
        loader = InputLoader()
        
        try:
            contacts = loader.load_contacts(args.input)
            if args.input:
                print(f"Loaded {len(contacts)} contacts from {args.input}")
            else:
                print(f"Loaded {len(contacts)} hardcoded contacts")
        except (FileNotFoundError, ValidationError, ValueError) as e:
            print(f"ERROR: {e}")
            sys.exit(1)
        
        print()
        
        # Step 3: Initialize modules
        print("Initializing modules...")
        email_generator = EmailGenerator()
        preview_handler = PreviewHandler()
        email_sender = EmailSender(config)
        logger = Logger()
        print("Modules initialized")
        print()
        
        # Step 4: Connect to SMTP (unless dry-run)
        if not config.DRY_RUN:
            print("Connecting to SMTP server...")
            email_sender.connect()
            print()
        else:
            print("Running in DRY RUN mode - no emails will be sent")
            print()
        
        # Step 5: Process each contact
        stats = {
            "total": len(contacts),
            "sent": 0,
            "skipped": 0,
            "failed": 0
        }
        
        for i, contact in enumerate(contacts, 1):
            print(f"\nProcessing contact {i}/{len(contacts)}")
            print("-" * 60)
            
            try:
                # Generate email
                email = email_generator.generate_email(contact)
                
                # Validate email
                is_valid, error_msg = email_generator.validate_email(email)
                if not is_valid:
                    print(f"ERROR: Email validation failed: {error_msg}")
                    logger.log_failed(
                        recipient_email=contact['recipient_email'],
                        company=contact['company'],
                        role=contact['role'],
                        subject=email['subject'],
                        error_message=error_msg,
                        word_count=email_generator.get_word_count(email)
                    )
                    stats["failed"] += 1
                    continue
                
                # Preview email
                preview_handler.preview_email(contact, email)
                
                # Get user confirmation
                confirmation = preview_handler.get_confirmation()
                
                if confirmation == 'yes':
                    # Send email
                    success, error_msg = email_sender.send_email(
                        to=contact['recipient_email'],
                        subject=email['subject'],
                        body=email['body']
                    )
                    
                    if success:
                        logger.log_sent(
                            recipient_email=contact['recipient_email'],
                            company=contact['company'],
                            role=contact['role'],
                            subject=email['subject'],
                            word_count=email_generator.get_word_count(email)
                        )
                        stats["sent"] += 1
                    else:
                        logger.log_failed(
                            recipient_email=contact['recipient_email'],
                            company=contact['company'],
                            role=contact['role'],
                            subject=email['subject'],
                            error_message=error_msg,
                            word_count=email_generator.get_word_count(email)
                        )
                        stats["failed"] += 1
                
                elif confirmation == 'no':
                    # Skip this email
                    logger.log_skipped(
                        recipient_email=contact['recipient_email'],
                        company=contact['company'],
                        role=contact['role'],
                        subject=email['subject'],
                        word_count=email_generator.get_word_count(email)
                    )
                    stats["skipped"] += 1
                
                elif confirmation == 'skip':
                    # Skip this email
                    logger.log_skipped(
                        recipient_email=contact['recipient_email'],
                        company=contact['company'],
                        role=contact['role'],
                        subject=email['subject'],
                        word_count=email_generator.get_word_count(email)
                    )
                    stats["skipped"] += 1
            
            except Exception as e:
                print(f"ERROR: Failed to process contact: {e}")
                logger.log_failed(
                    recipient_email=contact['recipient_email'],
                    company=contact['company'],
                    role=contact['role'],
                    subject="",
                    error_message=str(e),
                    word_count=0
                )
                stats["failed"] += 1
        
        # Step 6: Disconnect from SMTP
        if not config.DRY_RUN:
            email_sender.disconnect()
        
        # Step 7: Display summary
        preview_handler.display_summary(
            total=stats["total"],
            sent=stats["sent"],
            skipped=stats["skipped"],
            failed=stats["failed"]
        )
        
        print(f"\nLog file created: {logger.log_file}")
        print("\nDone!")
    
    except ValueError as e:
        print(f"\nConfiguration Error: {e}")
        print("\nPlease check your .env file and ensure all required fields are set.")
        sys.exit(1)
    
    except FileNotFoundError as e:
        print(f"\nFile Error: {e}")
        print("\nPlease check that the input file exists and the path is correct.")
        sys.exit(1)
    
    except ValidationError as e:
        print(f"\nValidation Error: {e}")
        print("\nPlease check your input file data format.")
        sys.exit(1)
    
    except ConnectionError as e:
        print(f"\nConnection Error: {e}")
        print("\nPlease check your SMTP credentials and network connection.")
        sys.exit(1)
    
    except Exception as e:
        print(f"\nUnexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
