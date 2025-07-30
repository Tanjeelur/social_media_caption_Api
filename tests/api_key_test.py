import openai
import os
import dotenv
OPEN_API_KEY= os.getenv("OPENAI_API_KEY")

try:
    models = openai.models.list()
    print("✅ API key is valid.")
except openai.error.AuthenticationError:
    print("❌ Invalid API key.")
except Exception as e:
    print(f"⚠️ Other error occurred: {e}")