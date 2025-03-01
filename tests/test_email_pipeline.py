#!/usr/bin/env python3
"""
Test script for the Email Processing Pipeline

This script tests the email processing pipeline by:
1. Initializing the pipeline
2. Checking authentication status
3. Processing a small batch of emails
4. Verifying the results

Usage:
    python -m tests.test_email_pipeline
"""

import os
import sys
import unittest
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.email_pipeline import EmailPipeline

class TestEmailPipeline(unittest.TestCase):
    """Test cases for the Email Processing Pipeline"""
    
    def setUp(self):
        """Set up the test environment"""
        self.pipeline = EmailPipeline()
    
    def test_authentication(self):
        """Test if the Gmail service is authenticated"""
        is_authenticated = self.pipeline.is_authenticated()
        print(f"Gmail authentication status: {is_authenticated}")
        
        # This test may pass or fail depending on whether you've authenticated
        # with Gmail. It's mainly for informational purposes.
        if not is_authenticated:
            print("Gmail service is not authenticated.")
            print("Please run the web application and authenticate with Gmail first.")
            print("This test will be skipped.")
            self.skipTest("Gmail service not authenticated")
    
    def test_process_emails(self):
        """Test processing a small batch of emails"""
        # Skip if not authenticated
        if not self.pipeline.is_authenticated():
            self.skipTest("Gmail service not authenticated")
        
        # Process a small batch of emails
        max_emails = 3
        result = self.pipeline.process_emails(max_emails)
        
        print(f"Processing result: {result}")
        
        # Check if the processing was successful
        self.assertTrue(result["success"], "Email processing failed")
        
        # Note: The number of processed emails may be less than max_emails
        # if there are no new unread emails or if they've already been processed
        print(f"Processed {result['processed_emails']} emails")
        print(f"Created {result['created_capsules']} capsules")
        
        # Print the IDs of processed emails and created capsules
        if result.get("email_ids"):
            print("Processed email IDs:")
            for email_id in result["email_ids"]:
                print(f"  - {email_id}")
        
        if result.get("capsule_ids"):
            print("Created capsule IDs:")
            for capsule_id in result["capsule_ids"]:
                print(f"  - {capsule_id}")

if __name__ == "__main__":
    unittest.main() 