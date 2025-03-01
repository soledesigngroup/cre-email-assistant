import sys
import os
from datetime import datetime, timedelta
print("Starting database test...")


# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.db_utils import db_connection
from app.models.capsule import CapsuleModel

def test_database_connection():
    """Test basic database connectivity"""
    try:
        db = db_connection.connect()
        print("✅ Successfully connected to MongoDB")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return False

def test_capsule_crud():
    """Test basic CRUD operations for capsules"""
    # First connect to the database
    print("Connecting to database...")
    db = db_connection.connect()
    print(f"Database connection result: {db}")
    
    # Check what collections are available
    print("Available collections:")
    try:
        collections = db.list_collection_names()
        print(f"Collections: {collections}")
    except Exception as e:
        print(f"Error listing collections: {e}")
    
    # Get capsules collection
    print("Attempting to get capsules collection...")
    try:
        capsules = db_connection.get_collection("capsules")
        print(f"Capsules collection: {capsules}")
    except Exception as e:
        print(f"Error getting capsules collection: {e}")
    
    # Check if we have a valid collection object
    if capsules is None:
        print("❌ Failed to get capsules collection")
        return
    
    print("--- Testing Capsule Creation ---")
    
    # Sample data
    from datetime import datetime, timedelta
    
    sample_capsule = {
        "title": "123 Main St Property Inquiry",
        "type": "Property Inquiry",
        "status": "Active",
        "priority": 3,
        "entities": {
            "properties": [
                {
                    "name": "Downtown Office Building",
                    "address": "123 Main St, Anytown, USA",
                    "specs": {
                        "sq_ft": 25000,
                        "price_per_sq_ft": 28.5,
                        "property_type": "Office"
                    }
                }
            ],
            "people": [
                {
                    "name": "Jane Smith",
                    "email": "jane.smith@example.com",
                    "company": "ABC Investments",
                    "role": "Acquisition Manager"
                }
            ]
        },
        "summary": "Initial inquiry about the Downtown Office Building lease terms.",
        "follow_ups": [
            {
                "due_date": datetime.now() + timedelta(days=3),
                "description": "Send property brochure",
                "completed": False
            }
        ]
    }
    
    # Test create
    try:
        result = capsules.insert_one(sample_capsule)
        capsule_id = str(result.inserted_id)
        print(f"✅ Created capsule with ID: {capsule_id}")
    except Exception as e:
        print(f"❌ Error creating capsule: {e}")
        return
    
    # Test read
    print("\n--- Testing Capsule Retrieval ---")
    from bson.objectid import ObjectId
    retrieved_doc = capsules.find_one({"_id": ObjectId(capsule_id)})
    if retrieved_doc:
        print(f"✅ Retrieved capsule title: {retrieved_doc['title']}")
    else:
        print("❌ Failed to retrieve capsule")
    
    # Test update
    print("\n--- Testing Capsule Update ---")
    update_result = capsules.update_one(
        {"_id": ObjectId(capsule_id)},
        {"$set": {"title": "Updated: 123 Main St Inquiry", "priority": 4}}
    )
    print(f"✅ Update successful: {update_result.modified_count > 0}")
    
    # Verify update
    updated_doc = capsules.find_one({"_id": ObjectId(capsule_id)})
    if updated_doc:
        print(f"✅ Updated capsule title: {updated_doc['title']}")
        print(f"✅ Updated priority: {updated_doc['priority']}")
    
    # Test list
    print("\n--- Testing Capsule Listing ---")
    all_capsules = list(capsules.find({}))
    print(f"✅ Found {len(all_capsules)} capsules")
    
    # Clean up - uncomment to delete test data
    print("\n--- Cleaning Up ---")
    delete_result = capsules.delete_one({"_id": ObjectId(capsule_id)})
    print(f"✅ Delete successful: {delete_result.deleted_count > 0}")
    
    # Close connection
    db_connection.close()
    print("\n✅ Database tests completed successfully")

if __name__ == "__main__":
    test_capsule_crud()