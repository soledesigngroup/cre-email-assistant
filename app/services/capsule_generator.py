from typing import Dict, List, Any, Optional
from datetime import datetime
import re

from app.services.email_processor import EmailProcessor
from app.services.capsule_service import CapsuleService
from app.services.email_clustering import EmailClusteringService
from app.services.capsule_summary_service import CapsuleSummaryService
from app.services.follow_up_service import FollowUpService
from app.services.openai_service import OpenAIService
from app.models.email import EmailModel
from app.models.capsule import CapsuleModel

class CapsuleGenerator:
    """
    Service for generating capsules from processed emails:
    - Analyzes emails to determine if they should be grouped into capsules
    - Creates new capsules based on email content and extracted entities
    - Links related emails to existing capsules
    """
    
    def __init__(self, email_processor: EmailProcessor, capsule_service: CapsuleService, openai_service: OpenAIService):
        """
        Initialize the CapsuleGenerator
        
        Args:
            email_processor: EmailProcessor instance for accessing processed emails
            capsule_service: CapsuleService instance for creating and managing capsules
            openai_service: OpenAIService instance for AI-powered analysis
        """
        self.email_processor = email_processor
        self.capsule_service = capsule_service
        self.openai_service = openai_service
        self.clustering_service = EmailClusteringService(email_processor, openai_service)
        self.summary_service = CapsuleSummaryService(email_processor, openai_service)
        self.follow_up_service = FollowUpService(capsule_service, openai_service)
    
    def process_email(self, message_id: str) -> Optional[str]:
        """
        Process a single email and create/update capsules as needed
        
        Args:
            message_id: Gmail message ID of the email to process
            
        Returns:
            Capsule ID if a capsule was created or updated, None otherwise
        """
        # Get the processed email
        email_model = self.email_processor.get_email_by_id(message_id)
        if not email_model:
            print(f"Email with ID {message_id} not found")
            return None
        
        # Check if this email belongs to an existing thread that's already in a capsule
        thread_capsules = self.capsule_service.get_capsules_by_email(email_model.thread_id)
        if thread_capsules:
            # Add this email to the existing capsule
            capsule_id = str(thread_capsules[0]._id)
            self.capsule_service.add_email_to_capsule(capsule_id, message_id)
            
            # Update the capsule summary
            capsule = self.capsule_service.get_capsule(capsule_id)
            if capsule:
                new_summary = self.summary_service.update_capsule_summary(capsule)
                self.capsule_service.update_capsule(capsule_id, {"summary": new_summary})
                
            # Check for follow-ups
            follow_ups = self.follow_up_service.detect_follow_ups(email_model)
            if follow_ups:
                # Add follow-ups to the capsule
                if capsule and capsule.follow_ups:
                    # Append new follow-ups to existing ones
                    updated_follow_ups = capsule.follow_ups + follow_ups
                    self.capsule_service.update_capsule(capsule_id, {"follow_ups": updated_follow_ups})
                else:
                    # Set new follow-ups
                    self.capsule_service.update_capsule(capsule_id, {"follow_ups": follow_ups})
            
            # Check if this email completes any follow-ups
            completed_follow_ups = self.follow_up_service.detect_completed_follow_ups(email_model)
            if completed_follow_ups:
                print(f"Email {message_id} completed {len(completed_follow_ups)} follow-ups")
            
            return capsule_id
        
        # Use the AI-generated category to determine if we should create a capsule
        should_create, capsule_type = self._should_create_capsule(email_model)
        
        if should_create:
            # Create a new capsule
            capsule = self._create_capsule_from_email(email_model, capsule_type)
            capsule_id = self.capsule_service.create_capsule(capsule)
            
            # Link the email to the capsule
            if capsule_id:
                self.capsule_service.add_email_to_capsule(capsule_id, message_id)
                return capsule_id
        else:
            # Check if this email should be grouped with other emails based on clustering
            related_emails = self.clustering_service.get_related_emails(email_model)
            
            if related_emails:
                # Create a cluster with this email and related emails
                cluster = [email_model] + related_emails
                
                # Determine the capsule type based on the cluster
                cluster_type = self._determine_cluster_type(cluster)
                
                # Create a new capsule for the cluster
                capsule = self._create_capsule_from_cluster(cluster, cluster_type)
                capsule_id = self.capsule_service.create_capsule(capsule)
                
                # Link all emails in the cluster to the capsule
                if capsule_id:
                    self.capsule_service.add_email_to_capsule(capsule_id, message_id)
                    for related_email in related_emails:
                        self.capsule_service.add_email_to_capsule(capsule_id, related_email.message_id)
                    
                    return capsule_id
        
        return None
    
    def process_new_emails(self, max_emails: int = 10) -> List[str]:
        """
        Process new unread emails and create capsules as needed
        
        Args:
            max_emails: Maximum number of emails to process
            
        Returns:
            List of created capsule IDs
        """
        # Process new emails
        processed_ids = self.email_processor.process_new_emails(max_emails)
        
        # Create capsules for each processed email
        capsule_ids = []
        for message_id in processed_ids:
            capsule_id = self.process_email(message_id)
            if capsule_id and capsule_id not in capsule_ids:
                capsule_ids.append(capsule_id)
        
        return capsule_ids
    
    def process_email_clusters(self, days: int = 7, min_cluster_size: int = 2) -> List[str]:
        """
        Process recent emails to find clusters and create capsules
        
        Args:
            days: Number of days to look back for emails
            min_cluster_size: Minimum number of emails in a cluster
            
        Returns:
            List of created capsule IDs
        """
        # Get recent emails
        recent_emails = self.email_processor.get_recent_emails(days=days)
        
        # Skip emails that are already in capsules
        uncategorized_emails = []
        for email in recent_emails:
            capsules = self.capsule_service.get_capsules_by_email(email.message_id)
            if not capsules:
                uncategorized_emails.append(email)
        
        # Find clusters using different methods
        capsule_ids = []
        
        # 1. Cluster by thread
        thread_clusters = self.clustering_service.cluster_by_thread(uncategorized_emails)
        for thread_id, emails in thread_clusters.items():
            if len(emails) >= min_cluster_size:
                # Create a capsule for this thread cluster
                cluster_type = self._determine_cluster_type(emails)
                capsule = self._create_capsule_from_cluster(emails, cluster_type)
                capsule_id = self.capsule_service.create_capsule(capsule)
                
                # Link all emails to the capsule
                if capsule_id:
                    for email in emails:
                        self.capsule_service.add_email_to_capsule(capsule_id, email.message_id)
                    
                    capsule_ids.append(capsule_id)
        
        # 2. Cluster by entity overlap
        entity_clusters = self.clustering_service.cluster_by_entity_overlap(uncategorized_emails)
        for cluster in entity_clusters:
            if len(cluster) >= min_cluster_size:
                # Skip if all emails in this cluster are already in a capsule
                if all(email.message_id in [e.message_id for e in thread_clusters.get(email.thread_id, [])] for email in cluster):
                    continue
                
                # Create a capsule for this entity cluster
                cluster_type = self._determine_cluster_type(cluster)
                capsule = self._create_capsule_from_cluster(cluster, cluster_type)
                capsule_id = self.capsule_service.create_capsule(capsule)
                
                # Link all emails to the capsule
                if capsule_id:
                    for email in cluster:
                        self.capsule_service.add_email_to_capsule(capsule_id, email.message_id)
                    
                    capsule_ids.append(capsule_id)
        
        # 3. Cluster by subject similarity
        subject_clusters = self.clustering_service.cluster_by_subject(uncategorized_emails)
        for cluster in subject_clusters:
            if len(cluster) >= min_cluster_size:
                # Skip if all emails in this cluster are already in a capsule
                skip = True
                for email in cluster:
                    thread_emails = thread_clusters.get(email.thread_id, [])
                    thread_ids = [e.message_id for e in thread_emails]
                    entity_ids = []
                    for entity_cluster in entity_clusters:
                        entity_ids.extend([e.message_id for e in entity_cluster])
                    
                    if email.message_id not in thread_ids and email.message_id not in entity_ids:
                        skip = False
                        break
                
                if skip:
                    continue
                
                # Create a capsule for this subject cluster
                cluster_type = self._determine_cluster_type(cluster)
                capsule = self._create_capsule_from_cluster(cluster, cluster_type)
                capsule_id = self.capsule_service.create_capsule(capsule)
                
                # Link all emails to the capsule
                if capsule_id:
                    for email in cluster:
                        self.capsule_service.add_email_to_capsule(capsule_id, email.message_id)
                    
                    capsule_ids.append(capsule_id)
        
        return capsule_ids
    
    def _should_create_capsule(self, email_model: EmailModel) -> tuple:
        """
        Determine if an email should create a new capsule
        
        Args:
            email_model: EmailModel to analyze
            
        Returns:
            Tuple of (should_create: bool, capsule_type: str)
        """
        # Default values
        should_create = False
        
        # Use the AI-generated category if available
        if hasattr(email_model, 'category') and email_model.category:
            capsule_type = email_model.category
            
            # These categories should always create a capsule
            if email_model.category in ["Property", "Deal", "Task"]:
                should_create = True
            # For Meeting and General, create capsule only if priority is high enough
            elif email_model.category in ["Meeting", "General"] and email_model.priority <= 3:
                should_create = True
        else:
            # Fallback to the old logic if AI categorization is not available
            capsule_type = "General"
            
            # Check if email has property entities
            if email_model.extracted_data.get("properties"):
                should_create = True
                capsule_type = "Property"
            
            # Check if email subject contains keywords indicating a deal
            deal_keywords = ["offer", "contract", "purchase", "sale", "lease", "proposal", "deal", "transaction"]
            if any(keyword in email_model.subject.lower() for keyword in deal_keywords):
                should_create = True
                capsule_type = "Deal"
            
            # Check if email body contains follow-up indicators
            followup_patterns = [
                r'\bfollow(?:\s|-)?up\b',
                r'\baction(?:\s|-)?item\b',
                r'\btask\b',
                r'\bto-do\b',
                r'\bdeadline\b',
                r'\bdue\s+date\b'
            ]
            
            for pattern in followup_patterns:
                if re.search(pattern, email_model.body_text, re.IGNORECASE):
                    should_create = True
                    capsule_type = "Task"
                    break
        
        # Check if email is part of a long thread (indicating importance)
        thread_emails = self.email_processor.get_emails_by_thread(email_model.thread_id)
        if len(thread_emails) >= 3:
            should_create = True
            # Keep the existing capsule type if already set
        
        return should_create, capsule_type
    
    def _determine_cluster_type(self, emails: List[EmailModel]) -> str:
        """
        Determine the type of a cluster based on its emails
        
        Args:
            emails: List of EmailModel instances in the cluster
            
        Returns:
            Capsule type for the cluster
        """
        # Count the categories of emails in the cluster
        category_counts = {}
        for email in emails:
            if hasattr(email, 'category') and email.category:
                category = email.category
                category_counts[category] = category_counts.get(category, 0) + 1
        
        # If there's a dominant category, use it
        if category_counts:
            max_category = max(category_counts.items(), key=lambda x: x[1])
            if max_category[1] >= len(emails) / 2:  # If at least half the emails have this category
                return max_category[0]
        
        # Check for property entities
        has_property = False
        for email in emails:
            if email.extracted_data.get("properties"):
                has_property = True
                break
        
        if has_property:
            return "Property"
        
        # Check for deal keywords
        deal_keywords = ["offer", "contract", "purchase", "sale", "lease", "proposal", "deal", "transaction"]
        for email in emails:
            if any(keyword in email.subject.lower() for keyword in deal_keywords):
                return "Deal"
        
        # Check for task indicators
        task_patterns = [
            r'\bfollow(?:\s|-)?up\b',
            r'\baction(?:\s|-)?item\b',
            r'\btask\b',
            r'\bto-do\b',
            r'\bdeadline\b',
            r'\bdue\s+date\b'
        ]
        
        for email in emails:
            for pattern in task_patterns:
                if re.search(pattern, email.body_text, re.IGNORECASE):
                    return "Task"
        
        # Check for meeting indicators
        meeting_keywords = ["meeting", "call", "conference", "zoom", "teams", "webex", "hangout", "calendar"]
        for email in emails:
            if any(keyword in email.subject.lower() for keyword in meeting_keywords):
                return "Meeting"
        
        # Default to General
        return "General"
    
    def _create_capsule_from_email(self, email_model: EmailModel, capsule_type: str) -> CapsuleModel:
        """
        Create a new capsule from an email
        
        Args:
            email_model: EmailModel to create capsule from
            capsule_type: Type of capsule to create
            
        Returns:
            CapsuleModel instance
        """
        # Generate a title based on email subject and type
        title = email_model.subject
        
        # If it's a property capsule, include the property address in the title
        if capsule_type == "Property" and email_model.extracted_data.get("properties"):
            # Try to get the address from the first property
            property_data = email_model.extracted_data["properties"][0]
            property_address = property_data.get("address", property_data.get("value", ""))
            
            if property_address:
                title = f"{property_address} - {title}"
        
        # Create entities dictionary from extracted data
        entities = {
            "properties": email_model.extracted_data.get("properties", []),
            "people": email_model.extracted_data.get("people", []),
            "companies": email_model.extracted_data.get("companies", []),
            "dates": email_model.extracted_data.get("dates", [])
        }
        
        # Use the AI-generated summary if available, otherwise create a simple one
        if hasattr(email_model, 'summary') and email_model.summary:
            summary = email_model.summary
        else:
            summary = f"Created from email: {email_model.subject}"
        
        # Detect follow-ups
        follow_ups = self.follow_up_service.detect_follow_ups(email_model)
        
        # Use the AI-determined priority if available, otherwise calculate it
        if hasattr(email_model, 'priority') and email_model.priority:
            priority = email_model.priority
        else:
            priority = self._determine_priority(email_model)
        
        # Create the capsule
        capsule = CapsuleModel(
            title=title,
            type=capsule_type,
            status="Active",
            priority=priority,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            emails=[],  # Will be added after capsule creation
            entities=entities,
            summary=summary,
            follow_ups=follow_ups,
            user_notes=""
        )
        
        return capsule
    
    def _create_capsule_from_cluster(self, emails: List[EmailModel], capsule_type: str) -> CapsuleModel:
        """
        Create a new capsule from a cluster of emails
        
        Args:
            emails: List of EmailModel instances in the cluster
            capsule_type: Type of capsule to create
            
        Returns:
            CapsuleModel instance
        """
        # Sort emails by date
        emails.sort(key=lambda e: e.sent_at if e.sent_at else datetime.min)
        
        # Use the most recent email as the primary one
        primary_email = emails[-1]
        
        # Generate a title based on the primary email subject and type
        title = primary_email.subject
        
        # If it's a property capsule, include the property address in the title
        if capsule_type == "Property":
            # Look for property entities in all emails
            property_address = ""
            for email in emails:
                if email.extracted_data.get("properties"):
                    property_data = email.extracted_data["properties"][0]
                    property_address = property_data.get("address", property_data.get("value", ""))
                    if property_address:
                        break
            
            if property_address:
                title = f"{property_address} - {title}"
        
        # Merge entities from all emails
        merged_entities = {
            "properties": [],
            "people": [],
            "companies": [],
            "dates": []
        }
        
        # Track unique entities by name to avoid duplicates
        unique_properties = set()
        unique_people = set()
        unique_companies = set()
        unique_dates = set()
        
        for email in emails:
            # Add properties
            for prop in email.extracted_data.get("properties", []):
                if isinstance(prop, dict):
                    prop_name = prop.get("name", "").lower() or prop.get("address", "").lower()
                    if prop_name and prop_name not in unique_properties:
                        unique_properties.add(prop_name)
                        merged_entities["properties"].append(prop)
            
            # Add people
            for person in email.extracted_data.get("people", []):
                if isinstance(person, dict):
                    person_name = person.get("name", "").lower()
                    if person_name and person_name not in unique_people:
                        unique_people.add(person_name)
                        merged_entities["people"].append(person)
            
            # Add companies
            for company in email.extracted_data.get("companies", []):
                if isinstance(company, dict):
                    company_name = company.get("name", "").lower()
                    if company_name and company_name not in unique_companies:
                        unique_companies.add(company_name)
                        merged_entities["companies"].append(company)
            
            # Add dates
            for date_item in email.extracted_data.get("dates", []):
                if isinstance(date_item, dict):
                    date_value = date_item.get("date", "").lower() or date_item.get("value", "").lower()
                    if date_value and date_value not in unique_dates:
                        unique_dates.add(date_value)
                        merged_entities["dates"].append(date_item)
        
        # Create a temporary capsule to generate a summary
        temp_capsule = CapsuleModel(
            title=title,
            type=capsule_type,
            status="Active",
            priority=3,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            emails=[{"email_id": email.message_id, "added_at": datetime.utcnow()} for email in emails],
            entities=merged_entities,
            summary="",
            follow_ups=[],
            user_notes=""
        )
        
        # Generate a summary for the cluster
        summary = self.summary_service.generate_summary(temp_capsule)
        
        # Detect follow-ups from all emails
        all_follow_ups = []
        for email in emails:
            follow_ups = self.follow_up_service.detect_follow_ups(email)
            all_follow_ups.extend(follow_ups)
        
        # Deduplicate follow-ups by title
        unique_follow_ups = []
        follow_up_titles = set()
        
        for follow_up in all_follow_ups:
            if follow_up["title"] not in follow_up_titles:
                follow_up_titles.add(follow_up["title"])
                unique_follow_ups.append(follow_up)
        
        # Determine priority based on the highest priority email
        priority = min([self._determine_priority(email) for email in emails])
        
        # Create the capsule
        capsule = CapsuleModel(
            title=title,
            type=capsule_type,
            status="Active",
            priority=priority,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            emails=[],  # Will be added after capsule creation
            entities=merged_entities,
            summary=summary,
            follow_ups=unique_follow_ups,
            user_notes=""
        )
        
        return capsule
    
    def _determine_priority(self, email_model: EmailModel) -> int:
        """
        Determine priority level for a capsule based on email content
        
        Args:
            email_model: EmailModel to analyze
            
        Returns:
            Priority level (1-5, where 1 is highest priority)
        """
        # Default priority (medium)
        priority = 3
        
        # Check for high priority indicators
        high_priority_keywords = ["urgent", "important", "asap", "immediately", "deadline", "critical"]
        if any(keyword in email_model.subject.lower() for keyword in high_priority_keywords) or \
           any(keyword in email_model.body_text.lower() for keyword in high_priority_keywords):
            priority = 1
        
        # Check for medium-high priority indicators
        medium_high_keywords = ["soon", "priority", "attention", "needed", "required"]
        if priority == 3 and (any(keyword in email_model.subject.lower() for keyword in medium_high_keywords) or \
           any(keyword in email_model.body_text.lower() for keyword in medium_high_keywords)):
            priority = 2
        
        # Check for low priority indicators
        low_priority_keywords = ["fyi", "for your information", "update", "newsletter", "no action"]
        if any(keyword in email_model.subject.lower() for keyword in low_priority_keywords) or \
           any(keyword in email_model.body_text.lower() for keyword in low_priority_keywords):
            priority = 5
        
        return priority 