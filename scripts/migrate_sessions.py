import json
from db import db

sessions_col = db["sessions"]

# agar pehle se data hai, dobara migrate mat karo
if sessions_col.count_documents({}) > 0:
    print("Sessions already migrated. Skipping.")
    exit(0)

with open("session_history.json") as f:
    sessions = json.load(f)

if sessions:
    sessions_col.insert_many(sessions)
    print(f"Migrated {len(sessions)} sessions")
else:
    print("No sessions found")
