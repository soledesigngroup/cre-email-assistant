#!/usr/bin/env python3
"""
Test script for Entity Recognition

This script tests the entity recognition capabilities by:
1. Setting up the OpenAI service
2. Testing entity extraction on sample CRE emails
3. Testing email summarization
4. Testing email categorization

Usage:
    python -m tests.test_entity_recognition
"""

import os
import sys
import json
import unittest
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.openai_service import OpenAIService

# Sample CRE email for testing
SAMPLE_EMAIL = """
Subject: 123 Main Street Office Building - Lease Proposal

Hi John,

I hope this email finds you well. I wanted to follow up on our conversation last week about the office space at 123 Main Street.

Based on our discussion, I've prepared a lease proposal for your review:

Property: 123 Main Street, Suite 400
Size: 5,000 square feet
Lease Term: 5 years
Base Rent: $30 per square foot, NNN
Annual Increases: 3%
TI Allowance: $50 per square foot
Free Rent: 3 months

The landlord, ABC Properties Inc., is willing to accommodate your move-in date of January 15, 2023. They're also open to discussing the option to expand into the adjacent suite (Suite 401) in year 3 if your company continues to grow as projected.

Please review the attached proposal and let me know if you have any questions or would like to schedule a meeting to discuss further. I believe this is a great opportunity for XYZ Corporation given the location and amenities of the building.

I'll need your feedback by next Friday, October 20, 2022, to keep the space reserved for you.

Best regards,
Sarah Johnson
Commercial Real Estate Broker
Smith & Associates
Phone: (555) 123-4567
Email: sarah@smithassociates.com
"""

class TestEntityRecognition(unittest.TestCase):
    """Test cases for Entity Recognition"""
    
    def setUp(self):
        """Set up the test environment"""
        self.openai_service = OpenAIService()
        
        # Check if OpenAI API key is set
        if not self.openai_service.api_key:
            print("WARNING: OPENAI_API_KEY not found in environment variables")
            print("Please set the OPENAI_API_KEY environment variable to run these tests")
            self.skipTest("OpenAI API key not set")
    
    def test_entity_extraction(self):
        """Test entity extraction from a sample email"""
        print("\n=== Testing Entity Extraction ===")
        
        # Extract entities from the sample email
        extracted_data = self.openai_service.extract_entities(
            email_text=SAMPLE_EMAIL,
            email_subject="123 Main Street Office Building - Lease Proposal"
        )
        
        # Print the extracted entities in a readable format
        print(json.dumps(extracted_data, indent=2))
        
        # Verify that entities were extracted
        self.assertIsNotNone(extracted_data)
        self.assertIsInstance(extracted_data, dict)
        
        # Check for expected entity types
        expected_entity_types = ["properties", "people", "companies", "dates", "financial_details"]
        for entity_type in expected_entity_types:
            self.assertIn(entity_type, extracted_data, f"Missing entity type: {entity_type}")
        
        # Check for specific entities we expect to find
        if "properties" in extracted_data:
            property_values = [p.get("address", "") for p in extracted_data["properties"]]
            self.assertTrue(any("123 Main Street" in p for p in property_values), 
                           "Property address '123 Main Street' not found")
        
        if "people" in extracted_data:
            people_names = [p.get("name", "") for p in extracted_data["people"]]
            self.assertTrue(any("Sarah Johnson" in name for name in people_names), 
                           "Person 'Sarah Johnson' not found")
        
        if "companies" in extracted_data:
            company_names = [c.get("name", "") for c in extracted_data["companies"]]
            self.assertTrue(any("ABC Properties" in name for name in company_names), 
                           "Company 'ABC Properties' not found")
        
        if "financial_details" in extracted_data:
            financial_values = [f.get("amount", "") for f in extracted_data["financial_details"]]
            self.assertTrue(any("$30" in value for value in financial_values), 
                           "Financial detail '$30 per square foot' not found")
    
    def test_email_summary(self):
        """Test email summarization"""
        print("\n=== Testing Email Summarization ===")
        
        # Generate a summary of the sample email
        summary = self.openai_service.generate_email_summary(
            email_text=SAMPLE_EMAIL,
            email_subject="123 Main Street Office Building - Lease Proposal"
        )
        
        # Print the summary
        print(summary)
        
        # Verify that a summary was generated
        self.assertIsNotNone(summary)
        self.assertIsInstance(summary, str)
        self.assertTrue(len(summary) > 0)
        
        # Check for key terms we expect in the summary
        key_terms = ["lease", "proposal", "123 Main Street"]
        for term in key_terms:
            self.assertIn(term.lower(), summary.lower(), f"Summary missing key term: {term}")
    
    def test_email_categorization(self):
        """Test email categorization"""
        print("\n=== Testing Email Categorization ===")
        
        # Categorize the sample email
        category_data = self.openai_service.categorize_email(
            email_text=SAMPLE_EMAIL,
            email_subject="123 Main Street Office Building - Lease Proposal"
        )
        
        # Print the categorization results
        print(json.dumps(category_data, indent=2))
        
        # Verify that categorization was performed
        self.assertIsNotNone(category_data)
        self.assertIsInstance(category_data, dict)
        
        # Check for expected fields
        expected_fields = ["category", "priority", "explanation"]
        for field in expected_fields:
            self.assertIn(field, category_data, f"Missing field: {field}")
        
        # Verify the category is one of the expected values
        expected_categories = ["Property", "Deal", "Meeting", "Task", "General"]
        self.assertIn(category_data.get("category"), expected_categories, 
                     f"Category not in expected values: {category_data.get('category')}")
        
        # Verify the priority is in the expected range
        priority = category_data.get("priority")
        self.assertIsInstance(priority, int)
        self.assertTrue(1 <= priority <= 5, f"Priority not in range 1-5: {priority}")

if __name__ == "__main__":
    unittest.main() 