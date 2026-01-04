import cloudinary
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", override=True)

print("KEY =", os.getenv("CLOUDINARY_API_KEY"))
print("SECRET =", os.getenv("CLOUDINARY_API_SECRET"))

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

print("Cloudinary configured successfully")

