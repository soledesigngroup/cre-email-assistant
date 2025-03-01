import os
import time
from typing import Dict, List, Any, Optional

from app.services.gmail_service import GmailService
from app.services.email_processor import EmailProcessor
from app.services.capsule_generator import CapsuleGenerator
from app.services.capsule_service import CapsuleService

class EmailPipeline:
    """
    Orchestrates the email processing pipeline:
    - Fetches emails from Gmail
    - Processes emails to extract entities and information
    - Generates capsules from processed emails
    - Can be run as a one-time process or as a continuous background job
    """
    
    def __init__(self):
        """Initialize the email processing pipeline"""
        # Set up Gmail service
        credentials_path = os.environ.get('GMAIL_CREDENTIALS_PATH', 'client_secret.json')
        token_path = os.environ.get('GMAIL_TOKEN_PATH', 'token.pickle')
        scopes = ['https://www.googleapis.com/auth/gmail.readonly']
        
        self.gmail_service = GmailService(credentials_path, token_path, scopes)
        
        # Build the service if token exists
        self.gmail_service.build_service()
        
        # Set up other services
        self.email_processor = EmailProcessor(self.gmail_service)
        self.capsule_service = CapsuleService()
        self.capsule_generator = CapsuleGenerator(self.email_processor, self.capsule_service)
    
    def process_emails(self, max_emails: int = 10) -> Dict[str, Any]:
        """
        Process new emails and generate capsules
        
        Args:
            max_emails: Maximum number of emails to process
            
        Returns:
            Dictionary with processing results
        """
        if not self.gmail_service.service:
            return {
                "success": False,
                "error": "Gmail service not authenticated",
                "processed_emails": 0,
                "created_capsules": 0
            }
        
        try:
            # Process new emails
            processed_ids = self.email_processor.process_new_emails(max_emails)
            
            # Generate capsules
            capsule_ids = []
            for message_id in processed_ids:
                capsule_id = self.capsule_generator.process_email(message_id)
                if capsule_id and capsule_id not in capsule_ids:
                    capsule_ids.append(capsule_id)
            
            return {
                "success": True,
                "processed_emails": len(processed_ids),
                "created_capsules": len(capsule_ids),
                "email_ids": processed_ids,
                "capsule_ids": capsule_ids
            }
            
        except Exception as e:
            print(f"Error in email pipeline: {e}")
            return {
                "success": False,
                "error": str(e),
                "processed_emails": 0,
                "created_capsules": 0
            }
    
    def run_continuous(self, interval_seconds: int = 300, max_emails: int = 10) -> None:
        """
        Run the email processing pipeline continuously at specified intervals
        
        Args:
            interval_seconds: Time between processing runs (in seconds)
            max_emails: Maximum number of emails to process in each run
        """
        print(f"Starting continuous email processing (interval: {interval_seconds}s)")
        
        try:
            while True:
                print(f"Running email processing at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                result = self.process_emails(max_emails)
                
                if result["success"]:
                    print(f"Processed {result['processed_emails']} emails, created {result['created_capsules']} capsules")
                else:
                    print(f"Error processing emails: {result.get('error', 'Unknown error')}")
                
                # Sleep until next run
                print(f"Sleeping for {interval_seconds} seconds...")
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("Email processing stopped by user")
        except Exception as e:
            print(f"Error in continuous processing: {e}")
    
    def is_authenticated(self) -> bool:
        """Check if Gmail service is authenticated"""
        return self.gmail_service.service is not None
    
    def get_auth_url(self, redirect_uri: str) -> str:
        """Get the Gmail authentication URL"""
        auth_url, _ = self.gmail_service.get_authorization_url(redirect_uri)
        return auth_url 