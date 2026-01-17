"""
Gmail Email Filter Automation - Main Entry Point

Orchestrates the email filtering workflow:
1. Authenticates with Gmail API
2. Fetches unread emails
3. Classifies emails as spam or safe
4. Moves spam emails to trash (or simulates in DRY_RUN mode)
"""

import os
from dotenv import load_dotenv
from auth import authenticate
from gmail_service import GmailClient
from classifier import EmailClassifier
from googleapiclient.errors import HttpError


# DRY_RUN mode: Set to True to simulate without actually moving emails
DRY_RUN = True


def main():
    """
    Main function that orchestrates the email filtering process.
    """
    print("=" * 60)
    print("Gmail Email Filter Automation")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    print("Environment variables loaded.")
    
    # Authenticate with Gmail API
    try:
        print("\n[1/5] Authenticating with Gmail API...")
        credentials = authenticate()
        print("✓ Authentication successful")
    except FileNotFoundError as e:
        print(f"✗ Authentication failed: {e}")
        return
    except Exception as e:
        print(f"✗ Authentication error: {e}")
        return
    
    # Initialize Gmail client
    try:
        print("\n[2/5] Initializing Gmail client...")
        gmail_client = GmailClient(credentials)
        print("✓ Gmail client initialized")
    except Exception as e:
        print(f"✗ Failed to initialize Gmail client: {e}")
        return
    
    # Initialize email classifier
    print("\n[3/5] Initializing email classifier...")
    classifier = EmailClassifier()
    print("✓ Email classifier initialized")
    
    # Display DRY_RUN status
    if DRY_RUN:
        print("\n⚠ DRY_RUN mode is ENABLED - No emails will be moved to trash")
    else:
        print("\n⚠ DRY_RUN mode is DISABLED - Emails WILL be moved to trash")
    
    # Fetch unread messages
    try:
        print("\n[4/5] Fetching unread messages...")
        max_results = 10
        message_ids = gmail_client.fetch_unread_messages(max_results=max_results)
        print(f"✓ Found {len(message_ids)} unread message(s)")
        
        if not message_ids:
            print("\nNo unread messages to process. Exiting.")
            return
            
    except HttpError as e:
        print(f"✗ Failed to fetch messages: {e}")
        return
    except Exception as e:
        print(f"✗ Error fetching messages: {e}")
        return
    
    # Process each message
    print("\n[5/5] Processing messages...")
    print("-" * 60)
    
    spam_count = 0
    safe_count = 0
    error_count = 0
    
    for i, message_id in enumerate(message_ids, 1):
        try:
            print(f"\n[{i}/{len(message_ids)}] Processing message {message_id[:10]}...")
            
            # Get email content
            try:
                email_data = gmail_client.get_email_content(message_id)
                subject = email_data.get('subject', '(No Subject)')
                from_email = email_data.get('from_email', 'Unknown')
                
                print(f"  From: {from_email}")
                print(f"  Subject: {subject[:50]}...")
                
            except HttpError as e:
                print(f"  ✗ Failed to get email content: {e}")
                error_count += 1
                continue
            except Exception as e:
                print(f"  ✗ Error getting email content: {e}")
                error_count += 1
                continue
            
            # Classify email
            try:
                is_spam, confidence = classifier.analyze_email(
                    email_data['subject'],
                    email_data['body']
                )
                
                if is_spam:
                    spam_count += 1
                    print(f"  🚨 Classified as SPAM (confidence: {confidence:.2%})")
                    
                    # Move to trash or simulate
                    if DRY_RUN:
                        print(f"  [DRY_RUN] Would move email {message_id} to trash")
                    else:
                        try:
                            gmail_client.move_to_trash(message_id)
                            print(f"  ✓ Moved to trash")
                        except HttpError as e:
                            print(f"  ✗ Failed to move to trash: {e}")
                            error_count += 1
                        except Exception as e:
                            print(f"  ✗ Error moving to trash: {e}")
                            error_count += 1
                else:
                    safe_count += 1
                    print(f"  ✓ Classified as SAFE (confidence: {confidence:.2%})")
                    
            except Exception as e:
                print(f"  ✗ Classification error: {e}")
                error_count += 1
                continue
                
        except Exception as e:
            print(f"  ✗ Unexpected error processing message: {e}")
            error_count += 1
            continue
    
    # Summary
    print("\n" + "=" * 60)
    print("Processing Complete")
    print("=" * 60)
    print(f"Total messages processed: {len(message_ids)}")
    print(f"  - Spam: {spam_count}")
    print(f"  - Safe: {safe_count}")
    print(f"  - Errors: {error_count}")
    
    if DRY_RUN:
        print("\n⚠ DRY_RUN mode was enabled - No emails were actually moved")
        print("   Set DRY_RUN = False in main.py to enable actual filtering")
    else:
        print(f"\n✓ {spam_count} email(s) moved to trash")
    
    print("=" * 60)


if __name__ == '__main__':
    main()
