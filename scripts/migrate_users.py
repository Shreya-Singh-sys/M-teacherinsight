import json
from db import db

users_col = db["users"]

with open("users.json") as f:
    users = json.load(f)

if users:
    users_col.insert_many(users)
    print(f"Migrated {len(users)} users")
else:
    print("No users found")
