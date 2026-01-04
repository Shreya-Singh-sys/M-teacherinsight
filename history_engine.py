import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

class HistoryEngine:
    def __init__(self):
        print("🔌 Connecting to MongoDB...")
        self.client = MongoClient(MONGO_URI)
        self.client.admin.command("ping")

        # ✅ SAME DB AS URI
        self.db = self.client.get_default_database()
        self.collection = self.db["sessions"]

        print("✅ MongoDB Connected (Single Source)")

    def save_session(self, data):
        data["timestamp"] = datetime.utcnow()
        result = self.collection.insert_one(data)
        print(f"📦 Session saved to Mongo: {result.inserted_id}")
        return result.inserted_id

    def get_previous_session(self, teacher_id=None):
        if teacher_id:
            return self.collection.find_one(
                {"teacher_id": teacher_id},
                sort=[("timestamp", -1)]
            )
        return None
