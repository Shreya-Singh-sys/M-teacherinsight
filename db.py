import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000
)

db = client.get_database("TIE_DB")

# force ping
client.admin.command("ping")

print("MongoDB connected & ping successful")

