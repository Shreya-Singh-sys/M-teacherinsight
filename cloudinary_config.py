import cloudinary
import os
from dotenv import load_dotenv

"""
Media Storage Configuration
---------------------------
Current: Cloudinary (rapid prototyping, video handling)
Azure-ready: Azure Blob Storage (planned for production)

This file acts as a media service abstraction layer.
"""

load_dotenv(dotenv_path=".env", override=True)

# Environment variables
CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
API_KEY = os.getenv("CLOUDINARY_API_KEY")
API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

if not CLOUD_NAME or not API_KEY or not API_SECRET:
    raise ValueError("❌ Cloudinary environment variables not set")

# Configure Cloudinary
cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=API_KEY,
    api_secret=API_SECRET,
    secure=True
)

print("✅ Media service configured (Cloudinary – Azure Blob ready)")

