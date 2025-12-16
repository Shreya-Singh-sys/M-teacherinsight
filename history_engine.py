import os
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()

# Now import the rest
import pymongo
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = "mongodb+srv://vishwa177_db_user:Vishwa177@tiesquad.tvlhzmz.mongodb.net/teacherDB"

class HistoryEngine:
    def __init__(self):
        print("🔌 Connecting to MongoDB (Hackathon Mode)...")
        try:

            self.client = MongoClient(MONGO_URI)
            
            self.db = self.client["TeacherInsightDB"]
            self.collection = self.db["sessions"]
            
            # Test Connection
            self.client.admin.command('ping')
            print("✅ Successfully connected to MongoDB Atlas!")
            
        except Exception as e:
            print(f"❌ MongoDB Connection Error Details: {e}")
            self.collection = None 

    def save_session(self, session_data):
        if self.collection is None:
            print("⚠️ Database unavailable. Skipping save.")
            return

        if "timestamp" not in session_data:
            session_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            self.collection.insert_one(session_data)
            print("💾 Session saved to cloud database.")
        except Exception as e:
            print(f"⚠️ Failed to save to DB: {e}")

    def get_previous_session(self):
        if self.collection is None: return None
        try:
            last_session = self.collection.find_one(sort=[('_id', -1)])
            if last_session:
                last_session['_id'] = str(last_session['_id'])
                return last_session
        except:
            pass
        return None

    def get_all_history(self):
        if self.collection is None: return []
        try:
            cursor = self.collection.find().sort('_id', -1)
            history = []
            for doc in cursor:
                doc['_id'] = str(doc['_id'])
                history.append(doc)
            return history
        except:
            return []