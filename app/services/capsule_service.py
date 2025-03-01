from datetime import datetime
from typing import Dict, List, Optional, Any
from bson.objectid import ObjectId

from app.services.db_utils import db_connection
from app.models.capsule import CapsuleModel

class CapsuleService:
    def __init__(self):
        self.db = db_connection.connect()
        self.capsules = db_connection.get_collection("capsules")
    
    def create_capsule(self, capsule: CapsuleModel) -> str:
        """Create a new capsule and return its ID"""
        capsule_dict = capsule.to_dict()
        result = self.capsules.insert_one(capsule_dict)
        return str(result.inserted_id)
    
    def get_capsule(self, capsule_id: str) -> Optional[CapsuleModel]:
        """Get a capsule by ID"""
        result = self.capsules.find_one({"_id": ObjectId(capsule_id)})
        if result:
            return CapsuleModel.from_dict(result)
        return None
    
    def update_capsule(self, capsule_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a capsule and return success status"""
        update_data["updated_at"] = datetime.utcnow()
        result = self.capsules.update_one(
            {"_id": ObjectId(capsule_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def delete_capsule(self, capsule_id: str) -> bool:
        """Delete a capsule and return success status"""
        result = self.capsules.delete_one({"_id": ObjectId(capsule_id)})
        return result.deleted_count > 0
    
    def list_capsules(self, filters: Dict[str, Any] = None, limit: int = 100) -> List[CapsuleModel]:
        """List capsules with optional filtering"""
        filters = filters or {}
        cursor = self.capsules.find(filters).limit(limit)
        
        capsules = []
        for doc in cursor:
            capsule = CapsuleModel.from_dict(doc)
            capsules.append(capsule)
        
        return capsules
    
    def add_email_to_capsule(self, capsule_id: str, email_id: str) -> bool:
        """Add an email reference to a capsule"""
        result = self.capsules.update_one(
            {"_id": ObjectId(capsule_id)},
            {
                "$push": {"emails": {"email_id": email_id, "added_at": datetime.utcnow()}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    
    def get_capsules_by_email(self, email_id: str) -> List[CapsuleModel]:
        """Get all capsules that contain a specific email"""
        cursor = self.capsules.find({"emails.email_id": email_id})
        
        capsules = []
        for doc in cursor:
            capsule = CapsuleModel.from_dict(doc)
            capsules.append(capsule)
            
        return capsules
    
    def get_capsules_by_property(self, property_name: str) -> List[CapsuleModel]:
        """Get all capsules related to a specific property"""
        cursor = self.capsules.find({"entities.properties.name": property_name})
        
        capsules = []
        for doc in cursor:
            capsule = CapsuleModel.from_dict(doc)
            capsules.append(capsule)
            
        return capsules
    
    def get_capsules_by_type(self, capsule_type: str) -> List[CapsuleModel]:
        """Get all capsules of a specific type"""
        cursor = self.capsules.find({"type": capsule_type})
        
        capsules = []
        for doc in cursor:
            capsule = CapsuleModel.from_dict(doc)
            capsules.append(capsule)
            
        return capsules
    
    def get_pending_follow_ups(self) -> List[Dict[str, Any]]:
        """Get all capsules with pending follow-ups"""
        now = datetime.utcnow()
        cursor = self.capsules.find({
            "follow_ups": {
                "$elemMatch": {
                    "completed": False,
                    "due_date": {"$lte": now}
                }
            }
        })
        
        follow_ups = []
        for doc in cursor:
            capsule = CapsuleModel.from_dict(doc)
            for follow_up in capsule.follow_ups:
                if not follow_up.get("completed", False) and follow_up.get("due_date", now) <= now:
                    follow_up["capsule_id"] = str(doc["_id"])
                    follow_up["capsule_title"] = capsule.title
                    follow_ups.append(follow_up)
                    
        return follow_ups