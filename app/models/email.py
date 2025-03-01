from typing import Dict, List, Any, Optional
from datetime import datetime

class EmailModel:
    """
    Data model representing an Email in the CRE Email Assistant.
    This provides type hints and structure for working with Emails.
    """
    
    def __init__(
        self,
        message_id: str,
        thread_id: str,
        sender: Dict[str, str],
        recipients: List[Dict[str, str]],
        subject: str,
        body_text: str,
        body_html: str = "",
        sent_at: datetime = None,
        received_at: datetime = None,
        attachments: List[Dict[str, Any]] = None,
        capsule_ids: List[str] = None,
        is_read: bool = False,
        labels: List[str] = None,
        extracted_data: Dict[str, Any] = None,
        summary: str = "",
        category: str = "General",
        priority: int = 3,
        category_explanation: str = ""
    ):
        self.message_id = message_id
        self.thread_id = thread_id
        self.sender = sender
        self.recipients = recipients
        self.subject = subject
        self.body_text = body_text
        self.body_html = body_html
        self.sent_at = sent_at
        self.received_at = received_at or datetime.utcnow()
        self.attachments = attachments or []
        self.capsule_ids = capsule_ids or []
        self.is_read = is_read
        self.labels = labels or []
        self.extracted_data = extracted_data or {}
        self.summary = summary
        self.category = category
        self.priority = priority
        self.category_explanation = category_explanation
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert Email to dictionary for MongoDB storage"""
        return {
            "message_id": self.message_id,
            "thread_id": self.thread_id,
            "sender": self.sender,
            "recipients": self.recipients,
            "subject": self.subject,
            "body_text": self.body_text,
            "body_html": self.body_html,
            "sent_at": self.sent_at,
            "received_at": self.received_at,
            "attachments": self.attachments,
            "capsule_ids": self.capsule_ids,
            "is_read": self.is_read,
            "labels": self.labels,
            "extracted_data": self.extracted_data,
            "summary": self.summary,
            "category": self.category,
            "priority": self.priority,
            "category_explanation": self.category_explanation
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmailModel':
        """Create Email instance from dictionary (e.g., from MongoDB)"""
        return cls(
            message_id=data.get("message_id", ""),
            thread_id=data.get("thread_id", ""),
            sender=data.get("sender", {"name": "", "email": ""}),
            recipients=data.get("recipients", []),
            subject=data.get("subject", ""),
            body_text=data.get("body_text", ""),
            body_html=data.get("body_html", ""),
            sent_at=data.get("sent_at"),
            received_at=data.get("received_at"),
            attachments=data.get("attachments", []),
            capsule_ids=data.get("capsule_ids", []),
            is_read=data.get("is_read", False),
            labels=data.get("labels", []),
            extracted_data=data.get("extracted_data", {}),
            summary=data.get("summary", ""),
            category=data.get("category", "General"),
            priority=data.get("priority", 3),
            category_explanation=data.get("category_explanation", "")
        )