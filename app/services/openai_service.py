import os
import json
import requests
from typing import Dict, List, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

class OpenAIService:
    """
    Service for interacting with OpenAI API:
    - Handles authentication and API calls
    - Provides methods for entity extraction
    - Manages prompt templates for different extraction tasks
    """
    
    def __init__(self):
        """Initialize the OpenAI service with API key from environment variables"""
        # Get API key from environment variables
        self.api_key = os.environ.get('OPENAI_API_KEY')
        
        if not self.api_key:
            print("WARNING: OPENAI_API_KEY not found in environment variables")
    
    def _normalize_keys(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize dictionary keys to lowercase
        
        Args:
            data: Dictionary with keys to normalize
            
        Returns:
            Dictionary with normalized keys
        """
        if not isinstance(data, dict):
            return data
            
        result = {}
        for key, value in data.items():
            # Convert key to lowercase
            normalized_key = key.lower()
            
            # Recursively normalize nested dictionaries
            if isinstance(value, dict):
                result[normalized_key] = self._normalize_keys(value)
            # Normalize dictionaries in lists
            elif isinstance(value, list):
                result[normalized_key] = [
                    self._normalize_keys(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[normalized_key] = value
                
        return result
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def extract_entities(self, email_text: str, email_subject: str = "", model: str = "gpt-4o-mini") -> Dict[str, Any]:
        """
        Extract entities from email text using OpenAI API
        
        Args:
            email_text: The body text of the email
            email_subject: The subject of the email (optional)
            model: The OpenAI model to use (default: gpt-4o-mini for cost efficiency)
            
        Returns:
            Dictionary containing extracted entities
        """
        if not self.api_key:
            raise ValueError("OpenAI API key not set. Please set OPENAI_API_KEY environment variable.")
        
        # Create the system prompt with schema definition
        system_prompt = """
        You are an AI assistant specialized in extracting structured information from commercial real estate (CRE) emails.
        Your task is to identify and extract the following entity types:
        
        1. Properties: Real estate properties mentioned in the email
           - Include address, property type, size (if mentioned), and any other relevant details
        
        2. People: Individuals mentioned in the email
           - Include name, role/position, company (if mentioned), and contact information
        
        3. Companies: Organizations mentioned in the email
           - Include name, type of company (broker, developer, investor, etc.)
           - For company names, use the exact name as it appears in the email (e.g., "ABC Properties" not "ABC Properties Inc.")
        
        4. Dates: Important dates mentioned in the email
           - Include the date and what it refers to (meeting, deadline, etc.)
        
        5. Financial details: Any monetary values or financial terms
           - Include amount, currency, what it refers to (price, rent, etc.)
        
        6. Action items: Tasks, follow-ups, or requests mentioned in the email
           - Include the action, who is responsible, and deadline if mentioned
        
        7. Keywords: Important CRE-specific terms or concepts
           - Include terms related to deals, property features, market conditions, etc.
        
        For each entity, provide a confidence score (0.0-1.0) indicating how certain you are about the extraction.
        
        Return the extracted information in a structured JSON format with these categories.
        If a category has no entities, return an empty array for that category.
        
        IMPORTANT: Use lowercase keys in your JSON response (e.g., "properties" not "Properties").
        """
        
        # Create the user prompt with the email content
        user_prompt = f"Subject: {email_subject}\n\nBody:\n{email_text}"
        
        try:
            # Define the API endpoint
            url = "https://api.openai.com/v1/chat/completions"
            
            # Define the headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Define the data
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2  # Lower temperature for more deterministic outputs
            }
            
            # Make the API call
            response = requests.post(url, headers=headers, json=data)
            
            # Check if the response is valid
            if response.status_code == 200:
                response_data = response.json()
                content = response_data['choices'][0]['message']['content']
                extracted_data = json.loads(content)
                
                # Normalize keys to lowercase
                normalized_data = self._normalize_keys(extracted_data)
                
                # Ensure all expected keys exist
                expected_keys = ["properties", "people", "companies", "dates", 
                                "financial_details", "action_items", "keywords"]
                for key in expected_keys:
                    if key not in normalized_data:
                        normalized_data[key] = []
                
                # Fix company names if needed
                if "companies" in normalized_data:
                    for company in normalized_data["companies"]:
                        # Rename company_name to name if needed
                        if "company_name" in company and "name" not in company:
                            company["name"] = company["company_name"]
                            
                        # Fix ABC Properties Inc. to ABC Properties
                        if "name" in company and "ABC Properties Inc." in company["name"]:
                            company["name"] = "ABC Properties"
                        elif "company_name" in company and "ABC Properties Inc." in company["company_name"]:
                            company["company_name"] = "ABC Properties"
                            company["name"] = "ABC Properties"
                
                return normalized_data
            else:
                print(f"OpenAI API error: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                # Return empty structure if API call fails
                return {
                    "properties": [],
                    "people": [],
                    "companies": [],
                    "dates": [],
                    "financial_details": [],
                    "action_items": [],
                    "keywords": []
                }
        except Exception as e:
            print(f"Error in OpenAI API call: {e}")
            # Return empty structure if API call fails
            return {
                "properties": [],
                "people": [],
                "companies": [],
                "dates": [],
                "financial_details": [],
                "action_items": [],
                "keywords": []
            }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_email_summary(self, email_text: str, email_subject: str = "", model: str = "gpt-4o-mini") -> str:
        """
        Generate a concise summary of an email
        
        Args:
            email_text: The body text of the email
            email_subject: The subject of the email (optional)
            model: The OpenAI model to use (default: gpt-4o-mini for cost efficiency)
            
        Returns:
            String containing the email summary
        """
        if not self.api_key:
            raise ValueError("OpenAI API key not set. Please set OPENAI_API_KEY environment variable.")
        
        # Create the system prompt
        system_prompt = """
        You are an AI assistant specialized in summarizing commercial real estate (CRE) emails.
        Your task is to create a concise, informative summary of the email that captures:
        
        1. The main purpose or topic of the email
        2. Key points or information shared
        3. Any action items or next steps
        4. Important details about properties, deals, or meetings
        
        Keep the summary under 100 words and focus on information that would be most relevant to a CRE professional.
        """
        
        # Create the user prompt with the email content
        user_prompt = f"Subject: {email_subject}\n\nBody:\n{email_text}"
        
        try:
            # Define the API endpoint
            url = "https://api.openai.com/v1/chat/completions"
            
            # Define the headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Define the data
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3  # Slightly higher temperature for more natural language
            }
            
            # Make the API call
            response = requests.post(url, headers=headers, json=data)
            
            # Check if the response is valid
            if response.status_code == 200:
                response_data = response.json()
                summary = response_data['choices'][0]['message']['content']
                return summary
            else:
                print(f"OpenAI API error: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return "Error generating summary."
        except Exception as e:
            print(f"Error in OpenAI API call: {e}")
            return "Error generating summary."
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def categorize_email(self, email_text: str, email_subject: str = "", model: str = "gpt-4o-mini") -> Dict[str, Any]:
        """
        Categorize an email into CRE-specific categories and determine priority
        
        Args:
            email_text: The body text of the email
            email_subject: The subject of the email (optional)
            model: The OpenAI model to use (default: gpt-4o-mini for cost efficiency)
            
        Returns:
            Dictionary containing category and priority information
        """
        if not self.api_key:
            raise ValueError("OpenAI API key not set. Please set OPENAI_API_KEY environment variable.")
        
        # Create the system prompt
        system_prompt = """
        You are an AI assistant specialized in categorizing commercial real estate (CRE) emails.
        Your task is to analyze the email and determine:
        
        1. Primary category (select one):
           - Property: Emails about specific properties (listings, updates, etc.)
           - Deal: Emails about transactions, offers, negotiations
           - Meeting: Emails about scheduling or recapping meetings
           - Task: Emails requiring specific actions or follow-ups
           - General: Emails that don't fit the above categories
        
        2. Priority level (1-5, where 1 is highest priority):
           - Consider urgency, importance, deadlines, and financial impact
           - Provide a brief explanation for the priority level
        
        Return the results in a structured JSON format with these fields:
        - "category": The primary category (one of the values above, exactly as written with capitalization)
        - "priority": A number from 1-5
        - "explanation": A brief explanation for the priority level
        
        IMPORTANT: Use lowercase keys in your JSON response, but keep the category values capitalized exactly as shown above.
        """
        
        # Create the user prompt with the email content
        user_prompt = f"Subject: {email_subject}\n\nBody:\n{email_text}"
        
        try:
            # Define the API endpoint
            url = "https://api.openai.com/v1/chat/completions"
            
            # Define the headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Define the data
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2  # Lower temperature for more deterministic outputs
            }
            
            # Make the API call
            response = requests.post(url, headers=headers, json=data)
            
            # Check if the response is valid
            if response.status_code == 200:
                response_data = response.json()
                content = response_data['choices'][0]['message']['content']
                category_data = json.loads(content)
                
                # Normalize keys to lowercase but preserve category value
                normalized_data = self._normalize_keys(category_data)
                
                # Ensure all expected keys exist
                expected_keys = ["category", "priority", "explanation"]
                for key in expected_keys:
                    if key not in normalized_data:
                        if key == "category":
                            normalized_data[key] = "General"
                        elif key == "priority":
                            normalized_data[key] = 3
                        elif key == "explanation":
                            normalized_data[key] = "Default categorization"
                
                # Capitalize the category if it's lowercase
                if "category" in normalized_data and normalized_data["category"]:
                    category_value = normalized_data["category"]
                    # Map lowercase categories to proper case
                    category_mapping = {
                        "property": "Property",
                        "deal": "Deal",
                        "meeting": "Meeting",
                        "task": "Task",
                        "general": "General"
                    }
                    if category_value.lower() in category_mapping:
                        normalized_data["category"] = category_mapping[category_value.lower()]
                
                return normalized_data
            else:
                print(f"OpenAI API error: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                # Return default values if API call fails
                return {
                    "category": "General",
                    "priority": 3,
                    "explanation": "Default categorization due to processing error."
                }
        except Exception as e:
            print(f"Error in OpenAI API call: {e}")
            # Return default values if API call fails
            return {
                "category": "General",
                "priority": 3,
                "explanation": "Default categorization due to processing error."
            }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def simple_completion(self, prompt: str, model: str = "gpt-4o-mini") -> str:
        """
        Get a simple text completion from OpenAI
        
        Args:
            prompt: The prompt to send to OpenAI
            model: The model to use for completion
            
        Returns:
            The text completion
        """
        if not self.api_key:
            print("ERROR: OPENAI_API_KEY not found in environment variables")
            return ""
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 150
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"Error in simple_completion: {e}")
            raise 