import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

"""
Session History Engine
----------------------
Current: MongoDB (MongoDB API)
Azure-ready: Azure Cosmos DB (MongoDB API compatible)

Stores and retrieves teaching session analytics.
"""

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("❌ MONGO_URI not set in environment variables")

class HistoryEngine:
    def __init__(self):
        print("🔌 Connecting to Database...")
        self.client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000
        )

        # Safe connectivity check (cloud/container friendly)
        try:
            self.client.admin.command("ping")
            print("✅ Database ping successful")
        except Exception as e:
            print(f"⚠️ Database ping failed: {e}")

        # SAME DB as connection string
        self.db = self.client.get_default_database()
        self.collection = self.db["sessions"]

        print("✅ Session History Engine ready")

    def save_session(self, data):
        data["timestamp"] = datetime.utcnow()
        result = self.collection.insert_one(data)
        print(f"📦 Session saved: {result.inserted_id}")
        return result.inserted_id

    def get_previous_session(self, teacher_id=None):
        if teacher_id:
            return self.collection.find_one(
                {"teacher_id": teacher_id},
                sort=[("timestamp", -1)]
            )
        return None

