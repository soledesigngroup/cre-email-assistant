import os
from typing import Dict, List, Optional, Any
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

class MongoDBConnection:
    def __init__(self):
        # Use your Atlas connection string instead of localhost
        self.mongo_uri = os.getenv("MONGODB_URI", "mongodb+srv://ryanpower:Aa4ZCGW4yUX1w8Fm@creemailassistant.56dg2.mongodb.net/?retryWrites=true&w=majority&appName=CREEmailAssistant")
        self.client = None
        self.db = None
    
    def connect(self, db_name: str = "cre_email_assistant") -> Database:
        """Establish connection to MongoDB"""
        try:
            # Add tlsAllowInvalidCertificates=True to bypass SSL verification
            self.client = MongoClient(self.mongo_uri, tlsAllowInvalidCertificates=True)
            self.db = self.client[db_name]
            # Test connection
            self.client.admin.command('ping')
            print(f"Connected to MongoDB: {db_name}")
            return self.db
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            raise
    
    def close(self) -> None:
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("MongoDB connection closed")
    
    def get_collection(self, collection_name: str) -> Collection:
        """Get a collection by name"""
        if self.db is None:
            raise ValueError("Database connection not established. Call connect() first.")
        
        # Print debug info
        print(f"Getting collection: {collection_name}")
        print(f"Database: {self.db}")
        
        # Direct access to collection
        collection = self.db[collection_name]
        print(f"Collection reference: {collection}")
        
        return collection

# Singleton instance for app-wide use
db_connection = MongoDBConnection()