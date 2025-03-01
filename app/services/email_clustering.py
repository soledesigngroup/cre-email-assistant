from typing import Dict, List, Any, Optional
import re
from datetime import datetime, timedelta
from collections import defaultdict

from app.models.email import EmailModel
from app.services.email_processor import EmailProcessor
from app.services.openai_service import OpenAIService

class EmailClusteringService:
    """
    Service for clustering related emails into groups for capsule creation:
    - Groups emails by thread ID
    - Clusters emails by subject similarity
    - Clusters emails by entity overlap (properties, people, companies)
    - Uses semantic similarity to find related emails
    """
    
    def __init__(self, email_processor: EmailProcessor, openai_service: OpenAIService):
        """
        Initialize the EmailClusteringService
        
        Args:
            email_processor: EmailProcessor instance for accessing processed emails
            openai_service: OpenAIService instance for semantic analysis
        """
        self.email_processor = email_processor
        self.openai_service = openai_service
    
    def cluster_by_thread(self, emails: List[EmailModel]) -> Dict[str, List[EmailModel]]:
        """
        Group emails by thread ID
        
        Args:
            emails: List of EmailModel instances to cluster
            
        Returns:
            Dictionary mapping thread IDs to lists of emails
        """
        thread_clusters = defaultdict(list)
        
        for email in emails:
            thread_clusters[email.thread_id].append(email)
            
        return dict(thread_clusters)
    
    def cluster_by_subject(self, emails: List[EmailModel], similarity_threshold: float = 0.7) -> List[List[EmailModel]]:
        """
        Cluster emails by subject similarity
        
        Args:
            emails: List of EmailModel instances to cluster
            similarity_threshold: Threshold for considering subjects similar (0.0-1.0)
            
        Returns:
            List of email clusters (each cluster is a list of EmailModel instances)
        """
        # Normalize subjects by removing prefixes like "Re:", "Fwd:", etc.
        def normalize_subject(subject):
            return re.sub(r'^(?:Re|Fwd|FW|RE|FWD):\s*', '', subject.strip()).lower()
        
        # Group emails by normalized subject
        subject_groups = defaultdict(list)
        for email in emails:
            normalized_subject = normalize_subject(email.subject)
            subject_groups[normalized_subject].append(email)
        
        # Create clusters from subject groups
        clusters = list(subject_groups.values())
        
        return clusters
    
    def cluster_by_entity_overlap(self, emails: List[EmailModel], min_overlap: int = 1) -> List[List[EmailModel]]:
        """
        Cluster emails by entity overlap (properties, people, companies)
        
        Args:
            emails: List of EmailModel instances to cluster
            min_overlap: Minimum number of overlapping entities required
            
        Returns:
            List of email clusters (each cluster is a list of EmailModel instances)
        """
        clusters = []
        processed_emails = set()
        
        for i, email1 in enumerate(emails):
            if email1.message_id in processed_emails:
                continue
                
            cluster = [email1]
            processed_emails.add(email1.message_id)
            
            # Extract entities from email1
            entities1 = set()
            
            # Add property names/addresses
            for prop in email1.extracted_data.get("properties", []):
                if isinstance(prop, dict):
                    entities1.add(prop.get("name", "").lower())
                    entities1.add(prop.get("address", "").lower())
            
            # Add people names
            for person in email1.extracted_data.get("people", []):
                if isinstance(person, dict):
                    entities1.add(person.get("name", "").lower())
            
            # Add company names
            for company in email1.extracted_data.get("companies", []):
                if isinstance(company, dict):
                    entities1.add(company.get("name", "").lower())
            
            # Remove empty strings
            entities1.discard("")
            
            # Compare with other emails
            for j, email2 in enumerate(emails[i+1:], i+1):
                if email2.message_id in processed_emails:
                    continue
                
                # Extract entities from email2
                entities2 = set()
                
                # Add property names/addresses
                for prop in email2.extracted_data.get("properties", []):
                    if isinstance(prop, dict):
                        entities2.add(prop.get("name", "").lower())
                        entities2.add(prop.get("address", "").lower())
                
                # Add people names
                for person in email2.extracted_data.get("people", []):
                    if isinstance(person, dict):
                        entities2.add(person.get("name", "").lower())
                
                # Add company names
                for company in email2.extracted_data.get("companies", []):
                    if isinstance(company, dict):
                        entities2.add(company.get("name", "").lower())
                
                # Remove empty strings
                entities2.discard("")
                
                # Check overlap
                overlap = len(entities1.intersection(entities2))
                if overlap >= min_overlap:
                    cluster.append(email2)
                    processed_emails.add(email2.message_id)
            
            if len(cluster) > 1:  # Only add clusters with multiple emails
                clusters.append(cluster)
        
        return clusters
    
    def cluster_by_semantic_similarity(self, emails: List[EmailModel], max_emails_per_batch: int = 10) -> List[List[EmailModel]]:
        """
        Cluster emails by semantic similarity using OpenAI embeddings
        
        Args:
            emails: List of EmailModel instances to cluster
            max_emails_per_batch: Maximum number of emails to process in a batch
            
        Returns:
            List of email clusters (each cluster is a list of EmailModel instances)
        """
        # This is a simplified implementation - in a real app, you'd use a more sophisticated
        # approach with vector embeddings and clustering algorithms
        
        # For now, we'll use a simple approach based on the OpenAI API to determine similarity
        clusters = []
        processed_emails = set()
        
        # Process emails in batches to avoid overwhelming the API
        for i in range(0, len(emails), max_emails_per_batch):
            batch = emails[i:i+max_emails_per_batch]
            
            for j, email1 in enumerate(batch):
                if email1.message_id in processed_emails:
                    continue
                    
                cluster = [email1]
                processed_emails.add(email1.message_id)
                
                # Compare with other emails in the batch
                for k, email2 in enumerate(batch[j+1:], j+1):
                    if email2.message_id in processed_emails:
                        continue
                    
                    # Use OpenAI to determine if emails are related
                    prompt = f"""
                    Determine if these two emails are semantically related and should be grouped together.
                    
                    Email 1:
                    Subject: {email1.subject}
                    Body: {email1.body_text[:500]}...
                    
                    Email 2:
                    Subject: {email2.subject}
                    Body: {email2.body_text[:500]}...
                    
                    Are these emails related to the same topic, property, deal, or task?
                    Answer with just 'yes' or 'no'.
                    """
                    
                    try:
                        response = self.openai_service.simple_completion(prompt)
                        if response and "yes" in response.lower():
                            cluster.append(email2)
                            processed_emails.add(email2.message_id)
                    except Exception as e:
                        print(f"Error determining semantic similarity: {e}")
                
                if len(cluster) > 1:  # Only add clusters with multiple emails
                    clusters.append(cluster)
        
        return clusters
    
    def get_related_emails(self, email_model: EmailModel, max_results: int = 5) -> List[EmailModel]:
        """
        Find emails related to the given email
        
        Args:
            email_model: EmailModel to find related emails for
            max_results: Maximum number of related emails to return
            
        Returns:
            List of related EmailModel instances
        """
        related_emails = []
        
        # First, get emails from the same thread
        thread_emails = self.email_processor.get_emails_by_thread(email_model.thread_id)
        for email in thread_emails:
            if email.message_id != email_model.message_id and email not in related_emails:
                related_emails.append(email)
        
        # If we don't have enough related emails, look for emails with similar entities
        if len(related_emails) < max_results:
            # Get all emails from the last 30 days
            recent_emails = self.email_processor.get_recent_emails(days=30)
            
            # Extract entities from the target email
            target_entities = set()
            
            # Add property names/addresses
            for prop in email_model.extracted_data.get("properties", []):
                if isinstance(prop, dict):
                    target_entities.add(prop.get("name", "").lower())
                    target_entities.add(prop.get("address", "").lower())
            
            # Add people names
            for person in email_model.extracted_data.get("people", []):
                if isinstance(person, dict):
                    target_entities.add(person.get("name", "").lower())
            
            # Add company names
            for company in email_model.extracted_data.get("companies", []):
                if isinstance(company, dict):
                    target_entities.add(company.get("name", "").lower())
            
            # Remove empty strings
            target_entities.discard("")
            
            # Find emails with overlapping entities
            for email in recent_emails:
                if email.message_id == email_model.message_id or email in related_emails:
                    continue
                
                # Extract entities from this email
                email_entities = set()
                
                # Add property names/addresses
                for prop in email.extracted_data.get("properties", []):
                    if isinstance(prop, dict):
                        email_entities.add(prop.get("name", "").lower())
                        email_entities.add(prop.get("address", "").lower())
                
                # Add people names
                for person in email.extracted_data.get("people", []):
                    if isinstance(person, dict):
                        email_entities.add(person.get("name", "").lower())
                
                # Add company names
                for company in email.extracted_data.get("companies", []):
                    if isinstance(company, dict):
                        email_entities.add(company.get("name", "").lower())
                
                # Remove empty strings
                email_entities.discard("")
                
                # Check overlap
                overlap = len(target_entities.intersection(email_entities))
                if overlap > 0:
                    related_emails.append(email)
                    
                    if len(related_emails) >= max_results:
                        break
        
        return related_emails[:max_results] 