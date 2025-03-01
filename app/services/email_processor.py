from typing import Dict, List, Any, Optional
import re
import email.utils
from datetime import datetime, timedelta
from email.header import decode_header

from app.services.gmail_service import GmailService
from app.services.db_utils import db_connection
from app.services.openai_service import OpenAIService
from app.models.email import EmailModel

class EmailProcessor:
    """
    Service for processing emails from Gmail:
    - Fetches emails from Gmail API
    - Parses and normalizes email data
    - Extracts entities and key information
    - Stores processed emails in the database
    """
    
    def __init__(self, gmail_service: GmailService):
        """
        Initialize the EmailProcessor with a Gmail service
        
        Args:
            gmail_service: An authenticated GmailService instance
        """
        self.gmail_service = gmail_service
        self.db = db_connection.connect()
        self.emails_collection = db_connection.get_collection("emails")
        self.openai_service = OpenAIService()
    
    def process_new_emails(self, max_emails: int = 10) -> List[str]:
        """
        Process new unread emails from Gmail
        
        Args:
            max_emails: Maximum number of emails to process
            
        Returns:
            List of processed email IDs
        """
        # Query for unread emails
        messages = self.gmail_service.list_messages(max_results=max_emails, query="is:unread")
        
        processed_ids = []
        for message in messages:
            message_id = message.get('id')
            
            # Check if email already exists in database
            existing = self.emails_collection.find_one({"message_id": message_id})
            if existing:
                continue
                
            # Process the email
            email_data = self.gmail_service.get_message_with_body(message_id)
            email_model = self._convert_to_email_model(email_data)
            
            if email_model:
                # Extract entities and information using OpenAI
                self._extract_entities_with_ai(email_model)
                
                # Generate summary using OpenAI
                self._generate_summary(email_model)
                
                # Categorize email using OpenAI
                self._categorize_email(email_model)
                
                # Store in database
                email_dict = email_model.to_dict()
                result = self.emails_collection.insert_one(email_dict)
                
                if result.inserted_id:
                    processed_ids.append(message_id)
        
        return processed_ids
    
    def _convert_to_email_model(self, email_data: Dict[str, Any]) -> Optional[EmailModel]:
        """
        Convert Gmail API email data to EmailModel
        
        Args:
            email_data: Email data from Gmail API
            
        Returns:
            EmailModel instance or None if conversion fails
        """
        try:
            # Parse sender
            sender_raw = email_data.get('from', '')
            sender_name, sender_email = self._parse_email_address(sender_raw)
            sender = {"name": sender_name, "email": sender_email}
            
            # Parse recipients
            recipients_raw = email_data.get('to', '')
            recipients = []
            
            # Handle multiple recipients
            for recipient in recipients_raw.split(','):
                if recipient.strip():
                    name, email_addr = self._parse_email_address(recipient.strip())
                    recipients.append({"name": name, "email": email_addr})
            
            # Parse date
            date_str = email_data.get('date', '')
            sent_at = None
            if date_str:
                try:
                    # Convert email date format to datetime
                    timestamp = email.utils.mktime_tz(email.utils.parsedate_tz(date_str))
                    sent_at = datetime.fromtimestamp(timestamp)
                except Exception as e:
                    print(f"Error parsing date: {e}")
                    sent_at = datetime.utcnow()
            
            # Get body content
            body = email_data.get('body', {})
            body_text = body.get('plain', '')
            body_html = body.get('html', '')
            
            # Create EmailModel
            email_model = EmailModel(
                message_id=email_data.get('id', ''),
                thread_id=email_data.get('thread_id', ''),
                sender=sender,
                recipients=recipients,
                subject=email_data.get('subject', ''),
                body_text=body_text,
                body_html=body_html,
                sent_at=sent_at,
                received_at=datetime.utcnow(),
                attachments=[],  # TODO: Handle attachments
                labels=email_data.get('labels', []),
                is_read=False
            )
            
            return email_model
            
        except Exception as e:
            print(f"Error converting email to model: {e}")
            return None
    
    def _parse_email_address(self, address_str: str) -> tuple:
        """
        Parse email address string into name and email components
        
        Args:
            address_str: Email address string (e.g., "John Doe <john@example.com>")
            
        Returns:
            Tuple of (name, email)
        """
        # Default values
        name = ""
        email_addr = ""
        
        try:
            # Try to parse with email.utils
            parsed = email.utils.parseaddr(address_str)
            name, email_addr = parsed
            
            # Decode name if needed
            if name:
                decoded_parts = []
                for part, encoding in decode_header(name):
                    if isinstance(part, bytes):
                        if encoding:
                            decoded_parts.append(part.decode(encoding))
                        else:
                            decoded_parts.append(part.decode('utf-8', errors='replace'))
                    else:
                        decoded_parts.append(part)
                name = ''.join(decoded_parts)
            
            # If no name but email exists, use email as name
            if not name and email_addr:
                name = email_addr.split('@')[0]
                
        except Exception as e:
            print(f"Error parsing email address '{address_str}': {e}")
            
            # Fallback: try regex extraction
            email_match = re.search(r'[\w\.-]+@[\w\.-]+', address_str)
            if email_match:
                email_addr = email_match.group(0)
                # Try to extract name
                name_match = re.search(r'^(.*?)<', address_str)
                if name_match:
                    name = name_match.group(1).strip()
                else:
                    name = email_addr.split('@')[0]
        
        return name, email_addr
    
    def _extract_entities_with_ai(self, email_model: EmailModel) -> None:
        """
        Extract entities and key information from email using OpenAI
        
        Args:
            email_model: EmailModel to extract entities from
            
        Returns:
            None (modifies email_model in place)
        """
        try:
            # Use OpenAI to extract entities
            extracted_data = self.openai_service.extract_entities(
                email_text=email_model.body_text,
                email_subject=email_model.subject
            )
            
            # Initialize extracted data structure if OpenAI fails
            if not extracted_data:
                extracted_data = {
                    "properties": [],
                    "people": [],
                    "companies": [],
                    "dates": [],
                    "financial_details": [],
                    "action_items": [],
                    "keywords": []
                }
            
            # Add sender and recipients to people if not already included
            self._add_email_participants_to_people(email_model, extracted_data)
            
            # Update the email model with extracted data
            email_model.extracted_data = extracted_data
            
        except Exception as e:
            print(f"Error extracting entities with AI: {e}")
            # Fall back to regex-based extraction
            self._extract_entities_with_regex(email_model)
    
    def _extract_entities_with_regex(self, email_model: EmailModel) -> None:
        """
        Extract entities using regex as a fallback method
        
        Args:
            email_model: EmailModel to extract entities from
            
        Returns:
            None (modifies email_model in place)
        """
        # Initialize extracted data
        extracted_data = {
            "properties": [],
            "people": [],
            "companies": [],
            "dates": [],
            "financial_details": [],
            "action_items": [],
            "keywords": []
        }
        
        # Extract property addresses (simple regex for now)
        property_patterns = [
            r'\d+\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Plaza|Plz|Square|Sq|Highway|Hwy|Parkway|Pkwy)\b',
            r'\d+\s+[A-Za-z0-9\s,]+(?:Unit|Apt|Apartment|Suite|Ste)\s+[A-Za-z0-9-]+',
        ]
        
        for pattern in property_patterns:
            matches = re.findall(pattern, email_model.body_text, re.IGNORECASE)
            for match in matches:
                if match not in [p.get("value") for p in extracted_data["properties"]]:
                    extracted_data["properties"].append({
                        "address": match,
                        "confidence": 0.7
                    })
        
        # Extract dates
        date_patterns = [
            r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?,\s+\d{4}\b',
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, email_model.body_text)
            for match in matches:
                if match not in [d.get("value") for d in extracted_data["dates"]]:
                    extracted_data["dates"].append({
                        "date": match,
                        "confidence": 0.8
                    })
        
        # Extract companies
        company_indicators = [
            r'\b(?:LLC|Inc|Corp|Corporation|Company|Co|Ltd|Limited)\b',
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:LLC|Inc|Corp|Corporation|Company|Co|Ltd|Limited)\b'
        ]
        
        for pattern in company_indicators:
            matches = re.findall(pattern, email_model.body_text)
            for match in matches:
                if match not in [c.get("name") for c in extracted_data["companies"]]:
                    extracted_data["companies"].append({
                        "name": match,
                        "confidence": 0.6
                    })
        
        # Extract financial details
        financial_patterns = [
            r'\$\d+(?:,\d{3})*(?:\.\d{2})?',
            r'\d+(?:,\d{3})*\s+dollars',
            r'\d+(?:\.\d{2})?\s*(?:USD|EUR|GBP)'
        ]
        
        for pattern in financial_patterns:
            matches = re.findall(pattern, email_model.body_text)
            for match in matches:
                extracted_data["financial_details"].append({
                    "amount": match,
                    "confidence": 0.7
                })
        
        # Add sender and recipients to people
        self._add_email_participants_to_people(email_model, extracted_data)
        
        # Update the email model with extracted data
        email_model.extracted_data = extracted_data
    
    def _add_email_participants_to_people(self, email_model: EmailModel, extracted_data: Dict[str, Any]) -> None:
        """
        Add email sender and recipients to the people list
        
        Args:
            email_model: The email model containing sender and recipients
            extracted_data: The dictionary of extracted data to update
            
        Returns:
            None (modifies extracted_data in place)
        """
        # Extract people (from recipients)
        for recipient in email_model.recipients:
            if recipient.get("name") and recipient.get("email"):
                person = {
                    "name": recipient.get("name"),
                    "email": recipient.get("email"),
                    "role": "recipient",
                    "confidence": 1.0
                }
                
                # Check if person already exists in the list
                if not any(p.get("email") == person["email"] for p in extracted_data["people"]):
                    extracted_data["people"].append(person)
        
        # Add sender as a person
        if email_model.sender.get("name") and email_model.sender.get("email"):
            person = {
                "name": email_model.sender.get("name"),
                "email": email_model.sender.get("email"),
                "role": "sender",
                "confidence": 1.0
            }
            
            # Check if sender already exists in the list
            if not any(p.get("email") == person["email"] for p in extracted_data["people"]):
                extracted_data["people"].append(person)
    
    def _generate_summary(self, email_model: EmailModel) -> None:
        """
        Generate a summary of the email using OpenAI
        
        Args:
            email_model: EmailModel to summarize
            
        Returns:
            None (modifies email_model in place)
        """
        try:
            # Use OpenAI to generate summary
            summary = self.openai_service.generate_email_summary(
                email_text=email_model.body_text,
                email_subject=email_model.subject
            )
            
            # Update the email model with the summary
            if summary and not summary.startswith("Error"):
                email_model.summary = summary
            else:
                # Fallback to a simple summary
                email_model.summary = f"Email from {email_model.sender.get('name', 'Unknown')} about {email_model.subject}"
                
        except Exception as e:
            print(f"Error generating summary: {e}")
            # Fallback to a simple summary
            email_model.summary = f"Email from {email_model.sender.get('name', 'Unknown')} about {email_model.subject}"
    
    def _categorize_email(self, email_model: EmailModel) -> None:
        """
        Categorize the email using OpenAI
        
        Args:
            email_model: EmailModel to categorize
            
        Returns:
            None (modifies email_model in place)
        """
        try:
            # Use OpenAI to categorize email
            category_data = self.openai_service.categorize_email(
                email_text=email_model.body_text,
                email_subject=email_model.subject
            )
            
            # Update the email model with category information
            if category_data:
                email_model.category = category_data.get("category", "General")
                email_model.priority = category_data.get("priority", 3)
                email_model.category_explanation = category_data.get("explanation", "")
            else:
                # Fallback to default values
                email_model.category = "General"
                email_model.priority = 3
                email_model.category_explanation = "Default categorization"
                
        except Exception as e:
            print(f"Error categorizing email: {e}")
            # Fallback to default values
            email_model.category = "General"
            email_model.priority = 3
            email_model.category_explanation = "Default categorization due to error"
    
    def get_email_by_id(self, message_id: str) -> Optional[EmailModel]:
        """
        Get a processed email by message ID
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            EmailModel if found, None otherwise
        """
        result = self.emails_collection.find_one({"message_id": message_id})
        if result:
            return EmailModel.from_dict(result)
        return None
    
    def get_emails_by_thread(self, thread_id: str) -> List[EmailModel]:
        """
        Get all emails in a thread
        
        Args:
            thread_id: Gmail thread ID
            
        Returns:
            List of EmailModel instances in the thread
        """
        cursor = self.emails_collection.find({"thread_id": thread_id})
        
        emails = []
        for doc in cursor:
            email_model = EmailModel.from_dict(doc)
            emails.append(email_model)
            
        return emails
    
    def get_recent_emails(self, days: int = 30) -> List[EmailModel]:
        """
        Get emails received within the specified number of days
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of EmailModel instances received within the specified period
        """
        # Calculate the cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Query for emails received after the cutoff date
        cursor = self.emails_collection.find({"received_at": {"$gte": cutoff_date}})
        
        emails = []
        for doc in cursor:
            email_model = EmailModel.from_dict(doc)
            emails.append(email_model)
            
        return emails
    
    def mark_email_as_read(self, message_id: str) -> bool:
        """
        Mark an email as read in the database
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Success status
        """
        result = self.emails_collection.update_one(
            {"message_id": message_id},
            {"$set": {"is_read": True}}
        )
        return result.modified_count > 0 