#!/usr/bin/env python3
"""
Alternative test script to check if the OpenAI API is working correctly.
This script uses a different approach to initialize the OpenAI client.
"""

import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_openai_api():
    """Test if the OpenAI API is working correctly using the legacy approach."""
    # Get API key from environment variables
    api_key = os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found in environment variables")
        print("Please set the OPENAI_API_KEY environment variable to run this test")
        return False
    
    print(f"API key found: {api_key[:5]}...{api_key[-4:]}")
    
    try:
        # Set the API key for the openai package (legacy approach)
        openai.api_key = api_key
        
        # Make a simple API call using the legacy approach
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt="Hello, world!",
            max_tokens=50
        )
        
        # Check if the response is valid
        if response and response.choices and response.choices[0].text:
            print("OpenAI API test successful!")
            print(f"Response: {response.choices[0].text.strip()}")
            return True
        else:
            print("OpenAI API test failed: Invalid response format")
            print(f"Response: {response}")
            return False
            
    except Exception as e:
        print(f"OpenAI API test failed: {e}")
        return False

if __name__ == "__main__":
    test_openai_api() 