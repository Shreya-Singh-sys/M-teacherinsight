from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["TIE_DB"]
col = db["sessions"]

res = col.insert_one({
    "test": "manual insert",
    "from": "terminal"
})

print("Inserted:", res.inserted_id)
