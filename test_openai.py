#!/usr/bin/env python3
"""
Simple test script to check if the OpenAI API is working correctly.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_openai_api():
    """Test if the OpenAI API is working correctly."""
    # Get API key from environment variables
    api_key = os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found in environment variables")
        print("Please set the OPENAI_API_KEY environment variable to run this test")
        return False
    
    print(f"API key found: {api_key[:5]}...{api_key[-4:]}")
    
    try:
        # Initialize the OpenAI client
        client = OpenAI()
        
        # Make a simple API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, world!"}
            ]
        )
        
        # Check if the response is valid
        if response and response.choices and response.choices[0].message:
            print("OpenAI API test successful!")
            print(f"Response: {response.choices[0].message.content}")
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