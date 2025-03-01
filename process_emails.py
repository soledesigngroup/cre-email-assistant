#!/usr/bin/env python3
"""
Email Processing Pipeline CLI

This script runs the email processing pipeline to fetch, process, and organize emails
into capsules. It can be run as a one-time process or as a continuous background job.

Usage:
    python process_emails.py [--continuous] [--interval=300] [--max-emails=10]

Options:
    --continuous    Run continuously at specified intervals
    --interval      Time between processing runs in seconds (default: 300)
    --max-emails    Maximum number of emails to process in each run (default: 10)
"""

import os
import sys
import argparse
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.email_pipeline import EmailPipeline

def main():
    """Main entry point for the email processing script"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Email Processing Pipeline")
    parser.add_argument("--continuous", action="store_true", help="Run continuously at specified intervals")
    parser.add_argument("--interval", type=int, default=300, help="Time between processing runs in seconds (default: 300)")
    parser.add_argument("--max-emails", type=int, default=10, help="Maximum number of emails to process in each run (default: 10)")
    args = parser.parse_args()
    
    # Initialize the email pipeline
    pipeline = EmailPipeline()
    
    # Check if Gmail service is authenticated
    if not pipeline.is_authenticated():
        print("Gmail service is not authenticated.")
        print("Please run the web application and authenticate with Gmail first.")
        sys.exit(1)
    
    # Run the pipeline
    if args.continuous:
        print(f"Running email processing pipeline continuously (interval: {args.interval}s, max emails: {args.max_emails})")
        pipeline.run_continuous(args.interval, args.max_emails)
    else:
        print(f"Running email processing pipeline once (max emails: {args.max_emails})")
        result = pipeline.process_emails(args.max_emails)
        
        if result["success"]:
            print(f"Successfully processed {result['processed_emails']} emails")
            print(f"Created {result['created_capsules']} capsules")
        else:
            print(f"Error processing emails: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main() 