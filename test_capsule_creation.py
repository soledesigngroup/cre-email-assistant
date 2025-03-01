import os
import sys
from datetime import datetime, timedelta

from app.services.gmail_service import GmailService
from app.services.email_processor import EmailProcessor
from app.services.capsule_service import CapsuleService
from app.services.capsule_generator import CapsuleGenerator
from app.services.openai_service import OpenAIService
from app.services.db_utils import db_connection

def test_capsule_creation():
    """
    Test the end-to-end capsule creation process:
    1. Process new emails
    2. Create capsules based on email content
    3. Cluster related emails
    4. Generate summaries
    5. Detect follow-ups
    """
    print("Initializing services...")
    
    # Initialize services
    # Set up Gmail service with required parameters
    credentials_path = os.environ.get('GMAIL_CREDENTIALS_PATH', 'client_secret.json')
    token_path = os.environ.get('GMAIL_TOKEN_PATH', 'token.pickle')
    scopes = ['https://www.googleapis.com/auth/gmail.readonly']
    
    gmail_service = GmailService(credentials_path, token_path, scopes)
    
    # Build the service if token exists
    try:
        gmail_service.build_service()
    except Exception as e:
        print(f"Error building Gmail service: {e}")
        print("You may need to authenticate first. Please run the authentication flow.")
        return
    
    email_processor = EmailProcessor(gmail_service)
    capsule_service = CapsuleService()
    openai_service = OpenAIService()
    capsule_generator = CapsuleGenerator(email_processor, capsule_service, openai_service)
    
    # Process new emails
    print("\nProcessing new emails...")
    processed_ids = email_processor.process_new_emails(max_emails=5)
    print(f"Processed {len(processed_ids)} new emails")
    
    # Create capsules from individual emails
    print("\nCreating capsules from individual emails...")
    capsule_ids = []
    for message_id in processed_ids:
        capsule_id = capsule_generator.process_email(message_id)
        if capsule_id and capsule_id not in capsule_ids:
            capsule_ids.append(capsule_id)
    
    print(f"Created {len(capsule_ids)} capsules from individual emails")
    
    # List the created capsules
    if capsule_ids:
        print("\nCreated capsules:")
        for capsule_id in capsule_ids:
            capsule = capsule_service.get_capsule(capsule_id)
            if capsule:
                print(f"- {capsule.title} (Type: {capsule.type}, Priority: {capsule.priority})")
                print(f"  Summary: {capsule.summary[:100]}...")
                if capsule.follow_ups:
                    print(f"  Follow-ups: {len(capsule.follow_ups)}")
                    for i, follow_up in enumerate(capsule.follow_ups[:2]):  # Show first 2 follow-ups
                        status = "COMPLETED" if follow_up.get("completed", False) else "PENDING"
                        print(f"    {i+1}. {follow_up.get('title', 'Task')} - {status}")
                print()
    
    # Process email clusters
    print("\nProcessing email clusters...")
    cluster_capsule_ids = capsule_generator.process_email_clusters(days=7, min_cluster_size=2)
    print(f"Created {len(cluster_capsule_ids)} capsules from email clusters")
    
    # List the created cluster capsules
    if cluster_capsule_ids:
        print("\nCreated cluster capsules:")
        for capsule_id in cluster_capsule_ids:
            capsule = capsule_service.get_capsule(capsule_id)
            if capsule:
                print(f"- {capsule.title} (Type: {capsule.type}, Priority: {capsule.priority})")
                print(f"  Summary: {capsule.summary[:100]}...")
                print(f"  Emails: {len(capsule.emails)}")
                if capsule.follow_ups:
                    print(f"  Follow-ups: {len(capsule.follow_ups)}")
                    for i, follow_up in enumerate(capsule.follow_ups[:2]):  # Show first 2 follow-ups
                        status = "COMPLETED" if follow_up.get("completed", False) else "PENDING"
                        print(f"    {i+1}. {follow_up.get('title', 'Task')} - {status}")
                print()
    
    # Get pending follow-ups
    print("\nPending follow-ups:")
    pending_follow_ups = capsule_service.get_pending_follow_ups()
    if pending_follow_ups:
        for follow_up in pending_follow_ups:
            print(f"- {follow_up.get('title', 'Task')} (Due: {follow_up.get('due_date')})")
            print(f"  Capsule: {follow_up.get('capsule_title', 'Unknown')}")
            print()
    else:
        print("No pending follow-ups found")

if __name__ == "__main__":
    test_capsule_creation() 