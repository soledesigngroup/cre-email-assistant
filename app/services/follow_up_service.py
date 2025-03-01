from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import re

from app.models.email import EmailModel
from app.models.capsule import CapsuleModel
from app.services.openai_service import OpenAIService
from app.services.capsule_service import CapsuleService

class FollowUpService:
    """
    Service for detecting and managing follow-ups:
    - Analyzes emails for follow-up requests
    - Creates follow-up tasks with due dates
    - Generates reminders for pending follow-ups
    - Detects completed follow-ups
    """
    
    def __init__(self, capsule_service: CapsuleService, openai_service: OpenAIService):
        """
        Initialize the FollowUpService
        
        Args:
            capsule_service: CapsuleService instance for accessing capsules
            openai_service: OpenAIService instance for analyzing emails
        """
        self.capsule_service = capsule_service
        self.openai_service = openai_service
    
    def detect_follow_ups(self, email_model: EmailModel) -> List[Dict[str, Any]]:
        """
        Detect follow-up tasks in an email
        
        Args:
            email_model: EmailModel to analyze
            
        Returns:
            List of follow-up tasks
        """
        follow_ups = []
        
        # Check if the email already has extracted action items
        if email_model.extracted_data.get("action_items"):
            for action_item in email_model.extracted_data["action_items"]:
                # Try to extract due date if available
                due_date = datetime.utcnow() + timedelta(days=7)  # Default to 7 days from now
                
                # Look for a deadline in the action item
                if isinstance(action_item, dict):
                    action_text = action_item.get("action", "")
                    deadline = action_item.get("deadline", "")
                    responsible = action_item.get("responsible", "")
                    
                    # Try to parse the deadline
                    if deadline:
                        try:
                            # This is a simplified approach - in a real app, you'd use a more robust date parser
                            due_date = datetime.strptime(deadline, "%Y-%m-%d")
                        except:
                            pass  # Keep the default date if parsing fails
                    
                    follow_ups.append({
                        "title": action_text or f"Follow up on: {email_model.subject}",
                        "description": f"Action item from email: {email_model.subject}",
                        "responsible": responsible,
                        "due_date": due_date,
                        "completed": False,
                        "created_at": datetime.utcnow(),
                        "email_id": email_model.message_id
                    })
        
        # If no action items were extracted, use AI to detect follow-ups
        if not follow_ups:
            follow_ups = self._detect_follow_ups_with_ai(email_model)
        
        # If AI detection failed, fall back to regex patterns
        if not follow_ups:
            follow_ups = self._detect_follow_ups_with_regex(email_model)
        
        return follow_ups
    
    def _detect_follow_ups_with_ai(self, email_model: EmailModel) -> List[Dict[str, Any]]:
        """Use AI to detect follow-ups in an email"""
        try:
            prompt = f"""
            Analyze this email and identify any follow-up tasks, action items, or requests.
            
            Subject: {email_model.subject}
            From: {email_model.sender.get('name', 'Unknown')} ({email_model.sender.get('email', '')})
            
            Email Body:
            {email_model.body_text[:1000]}...
            
            Extract any follow-up tasks with these details:
            1. Task description
            2. Who is responsible (if mentioned)
            3. Due date or deadline (if mentioned)
            
            Format your response as a JSON array of objects with these fields:
            [
                {{
                    "title": "Task description",
                    "responsible": "Person responsible",
                    "due_date": "YYYY-MM-DD" or ""
                }}
            ]
            
            If no follow-up tasks are found, return an empty array: []
            """
            
            response = self.openai_service.simple_completion(prompt, model="gpt-4o")
            
            # Parse the JSON response
            import json
            try:
                tasks = json.loads(response)
                
                # Convert to follow-up format
                follow_ups = []
                for task in tasks:
                    # Parse due date if provided
                    due_date = datetime.utcnow() + timedelta(days=7)  # Default to 7 days from now
                    if task.get("due_date"):
                        try:
                            due_date = datetime.strptime(task["due_date"], "%Y-%m-%d")
                        except:
                            pass  # Keep the default date if parsing fails
                    
                    follow_ups.append({
                        "title": task.get("title", f"Follow up on: {email_model.subject}"),
                        "description": f"Action item from email: {email_model.subject}",
                        "responsible": task.get("responsible", ""),
                        "due_date": due_date,
                        "completed": False,
                        "created_at": datetime.utcnow(),
                        "email_id": email_model.message_id
                    })
                
                return follow_ups
            except json.JSONDecodeError:
                print(f"Error parsing AI response as JSON: {response}")
                return []
        except Exception as e:
            print(f"Error detecting follow-ups with AI: {e}")
            return []
    
    def _detect_follow_ups_with_regex(self, email_model: EmailModel) -> List[Dict[str, Any]]:
        """Use regex patterns to detect follow-ups in an email"""
        follow_ups = []
        
        # Patterns to detect follow-up requests
        followup_patterns = [
            r'\bfollow(?:\s|-)?up\b',
            r'\baction(?:\s|-)?item\b',
            r'\btask\b',
            r'\bto-do\b',
            r'\bdeadline\b',
            r'\bdue\s+date\b',
            r'\bplease\s+(?:send|provide|get|prepare|review)\b',
            r'\blet\s+me\s+know\b',
            r'\bget\s+back\s+to\s+me\b',
            r'\brespond\s+by\b',
            r'\bby\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\bneed\s+(?:to|from)\s+you\b'
        ]
        
        # Check for follow-up patterns in the email body
        for pattern in followup_patterns:
            matches = re.finditer(pattern, email_model.body_text, re.IGNORECASE)
            
            for match in matches:
                # Extract the sentence containing the match
                start = max(0, email_model.body_text.rfind('.', 0, match.start()) + 1)
                end = email_model.body_text.find('.', match.end())
                if end == -1:
                    end = len(email_model.body_text)
                
                sentence = email_model.body_text[start:end].strip()
                
                # Create a follow-up task
                follow_ups.append({
                    "title": f"Follow up: {sentence[:100]}...",
                    "description": f"Detected in email: {email_model.subject}\n\nContext: {sentence}",
                    "responsible": "",  # Can't reliably extract this with regex
                    "due_date": datetime.utcnow() + timedelta(days=7),  # Default to 7 days from now
                    "completed": False,
                    "created_at": datetime.utcnow(),
                    "email_id": email_model.message_id
                })
        
        # Deduplicate follow-ups by title
        unique_follow_ups = []
        titles = set()
        
        for follow_up in follow_ups:
            if follow_up["title"] not in titles:
                titles.add(follow_up["title"])
                unique_follow_ups.append(follow_up)
        
        return unique_follow_ups[:3]  # Limit to 3 follow-ups to avoid noise
    
    def get_pending_follow_ups(self, days_overdue: int = 0) -> List[Dict[str, Any]]:
        """
        Get all pending follow-ups, optionally filtering by days overdue
        
        Args:
            days_overdue: Only include follow-ups that are at least this many days overdue
            
        Returns:
            List of pending follow-ups with capsule information
        """
        # Get the cutoff date
        cutoff_date = datetime.utcnow()
        if days_overdue > 0:
            cutoff_date = cutoff_date - timedelta(days=days_overdue)
        
        # Get all capsules with pending follow-ups
        pending_follow_ups = self.capsule_service.get_pending_follow_ups()
        
        # Filter by days overdue if needed
        if days_overdue > 0:
            pending_follow_ups = [
                follow_up for follow_up in pending_follow_ups
                if follow_up.get("due_date", datetime.utcnow()) <= cutoff_date
            ]
        
        return pending_follow_ups
    
    def mark_follow_up_completed(self, capsule_id: str, follow_up_index: int) -> bool:
        """
        Mark a follow-up as completed
        
        Args:
            capsule_id: ID of the capsule containing the follow-up
            follow_up_index: Index of the follow-up in the capsule's follow_ups list
            
        Returns:
            Success status
        """
        # Get the capsule
        capsule = self.capsule_service.get_capsule(capsule_id)
        if not capsule or not capsule.follow_ups or follow_up_index >= len(capsule.follow_ups):
            return False
        
        # Update the follow-up
        capsule.follow_ups[follow_up_index]["completed"] = True
        capsule.follow_ups[follow_up_index]["completed_at"] = datetime.utcnow()
        
        # Update the capsule
        update_data = {
            "follow_ups": capsule.follow_ups,
            "updated_at": datetime.utcnow()
        }
        
        return self.capsule_service.update_capsule(capsule_id, update_data)
    
    def detect_completed_follow_ups(self, email_model: EmailModel) -> List[Dict[str, Any]]:
        """
        Detect if an email completes any pending follow-ups
        
        Args:
            email_model: EmailModel to analyze
            
        Returns:
            List of completed follow-ups
        """
        # Get all capsules that this email might be related to
        related_capsules = []
        
        # Check if this email is part of a thread that's in a capsule
        thread_capsules = self.capsule_service.get_capsules_by_email(email_model.thread_id)
        related_capsules.extend(thread_capsules)
        
        # Check if this email mentions any properties that are in capsules
        if email_model.extracted_data.get("properties"):
            for prop in email_model.extracted_data["properties"]:
                if isinstance(prop, dict) and prop.get("name"):
                    property_capsules = self.capsule_service.get_capsules_by_property(prop["name"])
                    related_capsules.extend(property_capsules)
        
        # Deduplicate capsules
        unique_capsules = []
        capsule_ids = set()
        
        for capsule in related_capsules:
            if not hasattr(capsule, '_id'):
                continue
                
            capsule_id = str(capsule._id)
            if capsule_id not in capsule_ids:
                capsule_ids.add(capsule_id)
                unique_capsules.append(capsule)
        
        # Check each capsule for pending follow-ups that might be completed by this email
        completed_follow_ups = []
        
        for capsule in unique_capsules:
            if not capsule.follow_ups:
                continue
                
            for i, follow_up in enumerate(capsule.follow_ups):
                if follow_up.get("completed", False):
                    continue
                    
                # Check if this email completes the follow-up
                if self._check_if_email_completes_follow_up(email_model, follow_up):
                    # Mark the follow-up as completed
                    self.mark_follow_up_completed(str(capsule._id), i)
                    
                    # Add to the list of completed follow-ups
                    completed_follow_up = follow_up.copy()
                    completed_follow_up["capsule_id"] = str(capsule._id)
                    completed_follow_up["capsule_title"] = capsule.title
                    completed_follow_up["completed"] = True
                    completed_follow_up["completed_at"] = datetime.utcnow()
                    
                    completed_follow_ups.append(completed_follow_up)
        
        return completed_follow_ups
    
    def _check_if_email_completes_follow_up(self, email_model: EmailModel, follow_up: Dict[str, Any]) -> bool:
        """Check if an email completes a follow-up task"""
        # This is a simplified implementation - in a real app, you'd use more sophisticated
        # NLP techniques to determine if an email completes a follow-up
        
        # Extract the key terms from the follow-up title and description
        follow_up_text = f"{follow_up.get('title', '')} {follow_up.get('description', '')}"
        follow_up_terms = set(re.findall(r'\b\w+\b', follow_up_text.lower()))
        
        # Remove common words
        common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by", "from", "up", "about", "into", "over", "after"}
        follow_up_terms = follow_up_terms - common_words
        
        # Check if the email contains a significant number of the follow-up terms
        email_text = f"{email_model.subject} {email_model.body_text}"
        email_text_lower = email_text.lower()
        
        # Count how many follow-up terms are in the email
        matching_terms = sum(1 for term in follow_up_terms if term in email_text_lower)
        
        # If more than 50% of the terms match, consider it a potential completion
        if len(follow_up_terms) > 0 and matching_terms / len(follow_up_terms) >= 0.5:
            # Check for completion indicators
            completion_indicators = [
                "completed", "done", "finished", "resolved", "addressed", "taken care of",
                "here it is", "as requested", "as asked", "attached is", "please find",
                "i've completed", "i have completed", "task complete"
            ]
            
            if any(indicator in email_text_lower for indicator in completion_indicators):
                return True
        
        return False 