import os
import cloudinary
from dotenv import load_dotenv
from cloudinary import uploader

load_dotenv()

class CloudinaryConfig:
    cloudinary.config(
        cloud_name=os.getenv("CLOUD_NAME"),
        api_key=os.getenv("CLOUD_API_KEY"),
        api_secret=os.getenv("CLOUD_API_SECRET"),
    )

    @staticmethod
    def upload_to_cloudinary_student_answer(image_file):
        response = uploader.upload(image_file, folder="student_answer")
        return response.get("secure_url")

    @staticmethod
    def upload_to_cloudinary_chave(image_file):
        response = uploader.upload(image_file, folder="prova_chave")
        return response.get("secure_url")