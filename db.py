import os
from pymongo import MongoClient
from dotenv import load_dotenv

"""
Database Layer
--------------
Current: MongoDB Atlas (MongoDB API)
Azure-ready: Azure Cosmos DB (MongoDB API compatible)

No query-level changes required for migration.
"""

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("❌ MONGO_URI not found in environment variables")

# MongoDB / Cosmos DB (Mongo API) Client
client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000
)

# Database reference
db = client.get_database("TIE_DB")

# --------------------------------------------------
# Connectivity Check (safe for cloud startup)
# --------------------------------------------------
try:
    client.admin.command("ping")
    print("✅ Database connected & ping successful")
except Exception as e:
    print(f"⚠️ Database connection issue: {e}")
    # Do NOT crash app – backend can still start
