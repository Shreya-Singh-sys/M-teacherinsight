import json
import os
from datetime import datetime
from pymongo import MongoClient

# 👇 Put your Connection String here (No <brackets>!)
MONGO_URI = "mongodb+srv://vishwa177_db_user:Vishwa177@tiesquad.tvlhzmz.mongodb.net/teacherDB"
JSON_FILE = "session_history.json"

class HistoryEngine:
    def __init__(self):
        self.use_cloud = False
        try:
            print("🔌 Connecting to DB...")
            self.client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True, serverSelectionTimeoutMS=3000)
            self.client.admin.command('ping')
            self.collection = self.client["TIE_DB"]["sessions"]
            self.use_cloud = True
            print("✅ Cloud Connected")
        except:
            print("⚠️ Cloud Failed. Using Local Mode.")
            if not os.path.exists(JSON_FILE):
                with open(JSON_FILE, "w") as f: json.dump([], f)

    def save_session(self, data):
        data["timestamp"] = datetime.now().strftime("%Y-%m-%d")
        if self.use_cloud:
            try: self.collection.insert_one(data)
            except: self._save_local(data)
        else:
            self._save_local(data)

    def _save_local(self, data):
        with open(JSON_FILE, "r+") as f:
            hist = json.load(f)
            hist.append(data)
            f.seek(0)
            json.dump(hist, f)

    def get_previous_session(self):
        # Simply returns None for simplicity in this restart
        return None