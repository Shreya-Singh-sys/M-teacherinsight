from pymongo import MongoClient
from datetime import datetime

client = MongoClient(os.getenv("MONGO_URI"))
db = client["TIE_DB"]
sessions = db["sessions"]

doc = {
    "timestamp": datetime.now().strftime("%b %d, %Y"),
    "video": {
        "cloudinary_url": upload_result["secure_url"],
        "public_id": upload_result["public_id"]
    },
    "analysis": {
        "overall_score": 25
    }
}

res = sessions.insert_one(doc)
print("Mongo inserted ID:", res.inserted_id)
