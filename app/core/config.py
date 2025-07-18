# from pydantic_settings import BaseSettings
# from dotenv import load_dotenv
# import os

# load_dotenv()

# class Settings(BaseSettings):
#     OPENROUTER_API_KEY: str
#     OPENROUTER_MODEL: str = "mistralai/mistral-small-3.1-24b-instruct:free"

#     class Config:
#         env_file = ".env"

# settings = Settings()


# app/core/config.py

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env file

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GENINI_MODEL")
