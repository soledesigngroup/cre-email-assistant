from typing import Dict, List, Any, Optional
from datetime import datetime

from app.models.capsule import CapsuleModel
from app.models.email import EmailModel
from app.services.openai_service import OpenAIService
from app.services.email_processor import EmailProcessor

class CapsuleSummaryService:
    """
    Service for generating summaries for Capsules:
    - Creates concise summaries of email threads
    - Extracts key information from multiple emails
    - Updates summaries as new emails are added
    """
    
    def __init__(self, email_processor: EmailProcessor, openai_service: OpenAIService):
        """
        Initialize the CapsuleSummaryService
        
        Args:
            email_processor: EmailProcessor instance for accessing emails
            openai_service: OpenAIService instance for generating summaries
        """
        self.email_processor = email_processor
        self.openai_service = openai_service
    
    def generate_summary(self, capsule: CapsuleModel) -> str:
        """
        Generate a summary for a capsule based on its emails
        
        Args:
            capsule: CapsuleModel to generate summary for
            
        Returns:
            Generated summary text
        """
        # Get all emails in the capsule
        email_ids = [email_ref.get("email_id") for email_ref in capsule.emails]
        
        if not email_ids:
            return "No emails in this capsule."
        
        # Get email models
        emails = []
        for email_id in email_ids:
            email_model = self.email_processor.get_email_by_id(email_id)
            if email_model:
                emails.append(email_model)
        
        if not emails:
            return "No email content available."
        
        # Sort emails by sent_at date
        emails.sort(key=lambda e: e.sent_at if e.sent_at else datetime.min)
        
        # Generate summary based on capsule type
        if capsule.type == "Property":
            return self._generate_property_summary(capsule, emails)
        elif capsule.type == "Deal":
            return self._generate_deal_summary(capsule, emails)
        elif capsule.type == "Task":
            return self._generate_task_summary(capsule, emails)
        elif capsule.type == "Meeting":
            return self._generate_meeting_summary(capsule, emails)
        else:
            return self._generate_general_summary(capsule, emails)
    
    def _generate_property_summary(self, capsule: CapsuleModel, emails: List[EmailModel]) -> str:
        """Generate a summary for a Property capsule"""
        # Extract property information
        property_info = ""
        if capsule.entities.get("properties"):
            property_data = capsule.entities["properties"][0]
            property_address = property_data.get("address", property_data.get("value", ""))
            property_info = f"Property: {property_address}\n\n"
        
        # Create a prompt for the OpenAI API
        email_content = "\n\n".join([
            f"Email {i+1} - From: {email.sender.get('name', 'Unknown')} ({email.sender.get('email', '')})\n"
            f"Subject: {email.subject}\n"
            f"Date: {email.sent_at}\n\n"
            f"{email.body_text[:500]}..."  # Limit text to avoid token limits
            for i, email in enumerate(emails[:5])  # Limit to 5 emails
        ])
        
        prompt = f"""
        Create a concise summary of this email thread about a real estate property.
        
        {property_info}
        
        Email Thread:
        {email_content}
        
        Please include:
        1. Key property details (address, size, price if mentioned)
        2. Current status of discussions
        3. Any pending actions or decisions
        4. Timeline of key events
        
        Format the summary in clear paragraphs with bullet points for actions.
        """
        
        try:
            summary = self.openai_service.simple_completion(prompt, model="gpt-4o")
            return summary
        except Exception as e:
            print(f"Error generating property summary: {e}")
            return f"Summary generation failed. This capsule contains {len(emails)} emails about a property."
    
    def _generate_deal_summary(self, capsule: CapsuleModel, emails: List[EmailModel]) -> str:
        """Generate a summary for a Deal capsule"""
        # Extract deal information
        deal_info = ""
        if capsule.entities.get("properties"):
            property_data = capsule.entities["properties"][0]
            property_address = property_data.get("address", property_data.get("value", ""))
            deal_info = f"Property: {property_address}\n\n"
        
        # Create a prompt for the OpenAI API
        email_content = "\n\n".join([
            f"Email {i+1} - From: {email.sender.get('name', 'Unknown')} ({email.sender.get('email', '')})\n"
            f"Subject: {email.subject}\n"
            f"Date: {email.sent_at}\n\n"
            f"{email.body_text[:500]}..."  # Limit text to avoid token limits
            for i, email in enumerate(emails[:5])  # Limit to 5 emails
        ])
        
        prompt = f"""
        Create a concise summary of this email thread about a real estate deal.
        
        {deal_info}
        
        Email Thread:
        {email_content}
        
        Please include:
        1. Deal type (purchase, sale, lease, etc.)
        2. Key financial terms mentioned
        3. Current status of the deal
        4. Next steps and pending actions
        5. Key stakeholders involved
        
        Format the summary in clear paragraphs with bullet points for actions.
        """
        
        try:
            summary = self.openai_service.simple_completion(prompt, model="gpt-4o")
            return summary
        except Exception as e:
            print(f"Error generating deal summary: {e}")
            return f"Summary generation failed. This capsule contains {len(emails)} emails about a deal."
    
    def _generate_task_summary(self, capsule: CapsuleModel, emails: List[EmailModel]) -> str:
        """Generate a summary for a Task capsule"""
        # Create a prompt for the OpenAI API
        email_content = "\n\n".join([
            f"Email {i+1} - From: {email.sender.get('name', 'Unknown')} ({email.sender.get('email', '')})\n"
            f"Subject: {email.subject}\n"
            f"Date: {email.sent_at}\n\n"
            f"{email.body_text[:500]}..."  # Limit text to avoid token limits
            for i, email in enumerate(emails[:5])  # Limit to 5 emails
        ])
        
        # Include follow-ups in the prompt
        follow_ups_text = ""
        if capsule.follow_ups:
            follow_ups_text = "Current follow-up items:\n"
            for i, follow_up in enumerate(capsule.follow_ups):
                status = "COMPLETED" if follow_up.get("completed", False) else "PENDING"
                follow_ups_text += f"{i+1}. {follow_up.get('title', 'Task')} - {status}\n"
                if follow_up.get("description"):
                    follow_ups_text += f"   Description: {follow_up.get('description')}\n"
                if follow_up.get("due_date"):
                    follow_ups_text += f"   Due: {follow_up.get('due_date')}\n"
            follow_ups_text += "\n"
        
        prompt = f"""
        Create a concise summary of this email thread about tasks or action items.
        
        {follow_ups_text}
        
        Email Thread:
        {email_content}
        
        Please include:
        1. Main task or action item
        2. Who is responsible
        3. Current status
        4. Due dates or deadlines
        5. Any dependencies or blockers
        
        Format the summary in clear paragraphs with bullet points for actions.
        """
        
        try:
            summary = self.openai_service.simple_completion(prompt, model="gpt-4o")
            return summary
        except Exception as e:
            print(f"Error generating task summary: {e}")
            return f"Summary generation failed. This capsule contains {len(emails)} emails about tasks."
    
    def _generate_meeting_summary(self, capsule: CapsuleModel, emails: List[EmailModel]) -> str:
        """Generate a summary for a Meeting capsule"""
        # Create a prompt for the OpenAI API
        email_content = "\n\n".join([
            f"Email {i+1} - From: {email.sender.get('name', 'Unknown')} ({email.sender.get('email', '')})\n"
            f"Subject: {email.subject}\n"
            f"Date: {email.sent_at}\n\n"
            f"{email.body_text[:500]}..."  # Limit text to avoid token limits
            for i, email in enumerate(emails[:5])  # Limit to 5 emails
        ])
        
        prompt = f"""
        Create a concise summary of this email thread about a meeting.
        
        Email Thread:
        {email_content}
        
        Please include:
        1. Meeting purpose and topic
        2. Date, time, and location/format (if mentioned)
        3. Attendees (if mentioned)
        4. Key discussion points
        5. Action items or decisions
        
        Format the summary in clear paragraphs with bullet points for actions.
        """
        
        try:
            summary = self.openai_service.simple_completion(prompt, model="gpt-4o")
            return summary
        except Exception as e:
            print(f"Error generating meeting summary: {e}")
            return f"Summary generation failed. This capsule contains {len(emails)} emails about a meeting."
    
    def _generate_general_summary(self, capsule: CapsuleModel, emails: List[EmailModel]) -> str:
        """Generate a summary for a General capsule"""
        # Create a prompt for the OpenAI API
        email_content = "\n\n".join([
            f"Email {i+1} - From: {email.sender.get('name', 'Unknown')} ({email.sender.get('email', '')})\n"
            f"Subject: {email.subject}\n"
            f"Date: {email.sent_at}\n\n"
            f"{email.body_text[:500]}..."  # Limit text to avoid token limits
            for i, email in enumerate(emails[:5])  # Limit to 5 emails
        ])
        
        prompt = f"""
        Create a concise summary of this email thread.
        
        Email Thread:
        {email_content}
        
        Please include:
        1. Main topic or purpose of the conversation
        2. Key points discussed
        3. Any decisions made
        4. Any pending actions or next steps
        
        Format the summary in clear paragraphs with bullet points for actions.
        """
        
        try:
            summary = self.openai_service.simple_completion(prompt, model="gpt-4o")
            return summary
        except Exception as e:
            print(f"Error generating general summary: {e}")
            return f"Summary generation failed. This capsule contains {len(emails)} emails."
    
    def update_capsule_summary(self, capsule: CapsuleModel) -> str:
        """
        Update the summary of a capsule with new information
        
        Args:
            capsule: CapsuleModel to update summary for
            
        Returns:
            Updated summary text
        """
        # Generate a new summary
        new_summary = self.generate_summary(capsule)
        
        # Return the new summary
        return new_summary 