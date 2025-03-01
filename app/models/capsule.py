from typing import Dict, List, Any, Optional
from datetime import datetime

class CapsuleModel:
    """
    Data model representing a Capsule in the CRE Email Assistant.
    This provides type hints and structure for working with Capsules.
    """
    
    def __init__(
        self,
        title: str,
        type: str,
        status: str = "Active",
        priority: int = 3,
        created_at: datetime = None,
        updated_at: datetime = None,
        emails: List[Dict[str, Any]] = None,
        entities: Dict[str, List[Dict[str, Any]]] = None,
        summary: str = "",
        follow_ups: List[Dict[str, Any]] = None,
        user_notes: str = ""
    ):
        self.title = title
        self.type = type
        self.status = status
        self.priority = priority
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.emails = emails or []
        self.entities = entities or {
            "properties": [],
            "people": [],
            "companies": [],
            "dates": []
        }
        self.summary = summary
        self.follow_ups = follow_ups or []
        self.user_notes = user_notes
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert Capsule to dictionary for MongoDB storage"""
        return {
            "title": self.title,
            "type": self.type,
            "status": self.status,
            "priority": self.priority,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "emails": self.emails,
            "entities": self.entities,
            "summary": self.summary,
            "follow_ups": self.follow_ups,
            "user_notes": self.user_notes
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CapsuleModel':
        """Create Capsule instance from dictionary (e.g., from MongoDB)"""
        return cls(
            title=data.get("title", ""),
            type=data.get("type", ""),
            status=data.get("status", "Active"),
            priority=data.get("priority", 3),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            emails=data.get("emails", []),
            entities=data.get("entities", {"properties": [], "people": [], "companies": [], "dates": []}),
            summary=data.get("summary", ""),
            follow_ups=data.get("follow_ups", []),
            user_notes=data.get("user_notes", "")
        )