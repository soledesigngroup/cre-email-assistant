#!/usr/bin/env python3
"""
Direct test script to check if the OpenAI API is working correctly.
This script uses the OpenAI API directly with minimal dependencies.
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_openai_api_direct():
    """Test if the OpenAI API is working correctly using direct HTTP requests."""
    # Get API key from environment variables
    api_key = os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found in environment variables")
        print("Please set the OPENAI_API_KEY environment variable to run this test")
        return False
    
    print(f"API key found: {api_key[:5]}...{api_key[-4:]}")
    
    try:
        # Define the API endpoint
        url = "https://api.openai.com/v1/chat/completions"
        
        # Define the headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Define the data
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, world!"}
            ]
        }
        
        # Make the API call
        response = requests.post(url, headers=headers, json=data)
        
        # Check if the response is valid
        if response.status_code == 200:
            response_data = response.json()
            print("OpenAI API test successful!")
            print(f"Response: {response_data['choices'][0]['message']['content']}")
            return True
        else:
            print(f"OpenAI API test failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"OpenAI API test failed: {e}")
        return False

if __name__ == "__main__":
    test_openai_api_direct() 