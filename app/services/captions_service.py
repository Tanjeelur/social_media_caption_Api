# import os
# import httpx
# from app.models.captions import CaptionInput
# from app.core.config import settings

# async def call_openrouter(prompt: str) -> str:
#     headers = {
#         "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
#         "HTTP-Referer": "http://localhost",
#         "Content-Type": "application/json"
#     }

#     body = {
#         "model": settings.OPENROUTER_MODEL,
#         "messages": [{"role": "user", "content": prompt}]
#     }

#     async with httpx.AsyncClient() as client:
#         response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
#         response.raise_for_status()
#         return response.json()["choices"][0]["message"]["content"]

# def build_prompt(data: CaptionInput) -> str:
#     return f"""
# You are a social media expert helping businesses write captions.

# Business Type: {data.business_type}
# Post Description: {data.post_description}
# Season: {data.season}
# Location: {data.location or 'N/A'}

# Instructions:
# - Caption will be in English.
# - Generate a 2–3 line caption that reflects the season and location.
# - Encourage walk-ins, foot traffic, or engagement.
# - Add a fun or engaging tone.
# - Then, generate a list of 5–8 relevant, non-generic hashtags (no #love, #food, etc.).
# Return only the caption and a list of hashtags which will be in lower case.

# The output should be a JSON object with two keys: "caption" (string) and "hashtags" (array of strings).
#     Example:
#     {{
#         "caption": "This is a fantastic caption about my day!",
#         "hashtags": ["#goodvibes", "#happy", "#socialmedia"]
#     }}


# """


import os
import httpx
import json # Import the json module
from app.models.captions import CaptionInput
from app.core.config import settings

# Change the return type hint to dict
async def call_openrouter(prompt: str) -> dict:
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost", # Adjust this if your deployed app has a different domain
        "Content-Type": "application/json"
    }

    body = {
        "model": settings.OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        # Optional: Add response_format if OpenRouter supports it to explicitly request JSON
        # "response_format": {"type": "json_object"}
    }

    async with httpx.AsyncClient() as client:
        response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
        response.raise_for_status() # Raises an exception for 4xx/5xx responses

        llm_response_data = response.json()
        
        # The actual generated content is a string that should contain JSON
        content_string = llm_response_data["choices"][0]["message"]["content"]

        try:
            # Parse the content string as JSON
            parsed_content = json.loads(content_string)
            return parsed_content
        except json.JSONDecodeError as e:
            # Handle cases where the LLM might fail to return valid JSON
            print(f"Error decoding JSON from LLM: {e}")
            print(f"Raw LLM content: {content_string}")
            raise ValueError("LLM did not return valid JSON output.") from e

# Your build_prompt function remains excellent as is
def build_prompt(data: CaptionInput) -> str:
    return f"""
You are a social media expert helping businesses write captions.

Business Type: {data.business_type}
Post Description: {data.post_description}
Season: {data.season}
Location: {data.location or 'N/A'}

Instructions:
- Caption will be in English.
- Generate a 2–3 line caption that reflects the season and location.
- Encourage walk-ins, foot traffic, or engagement.
- Add a fun or engaging tone.
- Then, generate a list of 5–8 relevant, non-generic hashtags (no #love, #food, etc.).
- Hashtags should be in lower case.

The output should be a JSON object with two keys: "caption" (string) and "hashtags" (array of strings).
Example:
{{
    "caption": "This is a fantastic caption about my day!",
    "hashtags": ["#goodvibes", "#happy", "#socialmedia"]
}}
"""