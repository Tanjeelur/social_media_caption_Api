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
#-------------------------------------------------------------------------------------------------------------------------

# import os
# import httpx
# import json # Import the json module
# from app.models.captions import CaptionInput
# from app.core.config import settings

# # Change the return type hint to dict
# async def call_openrouter(prompt: str) -> dict:
#     headers = {
#         "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
#         "HTTP-Referer": "http://localhost", # Adjust this if your deployed app has a different domain
#         "Content-Type": "application/json"
#     }

#     body = {
#         "model": settings.OPENROUTER_MODEL,
#         "messages": [{"role": "user", "content": prompt}],
#         # Optional: Add response_format if OpenRouter supports it to explicitly request JSON
#         # "response_format": {"type": "json_object"}
#     }

#     async with httpx.AsyncClient() as client:
#         response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
#         response.raise_for_status() # Raises an exception for 4xx/5xx responses

#         llm_response_data = response.json()
        
#         # The actual generated content is a string that should contain JSON
#         content_string = llm_response_data["choices"][0]["message"]["content"]

#         try:
#             # Parse the content string as JSON
#             parsed_content = json.loads(content_string)
#             return parsed_content
#         except json.JSONDecodeError as e:
#             # Handle cases where the LLM might fail to return valid JSON
#             print(f"Error decoding JSON from LLM: {e}")
#             print(f"Raw LLM content: {content_string}")
#             raise ValueError("LLM did not return valid JSON output.") from e

# # Your build_prompt function remains excellent as is
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
# - Hashtags should be in lower case.

# The output should be a JSON object with two keys: "caption" (string) and "hashtags" (array of strings).
# Example:
# {{
#     "caption": "This is a fantastic caption about my day!",
#     "hashtags": ["#goodvibes", "#happy", "#socialmedia"]
# }}
# """








# call_openrouter.py
import os
import httpx
import json
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.core.config import GEMINI_API_KEY, GEMINI_MODEL
from app.models.captions import CaptionInput

GEMINI_API_KEY =GEMINI_API_KEY
#print(GEMINI_API_KEY)

# Define the Gemini model to use
GEMINI_MODEL = "gemini-2.0-flash" # Or another appropriate Gemini model

async def call_gemini_api(prompt: str) -> dict:
    """
    Calls the Gemini API to generate content based on the provided prompt.
    Expects and enforces JSON output from the LLM.
    """
    # Headers for Gemini API - Content-Type is important for structured responses
    headers = {
        "Content-Type": "application/json"
    }

    # The payload for the Gemini API call
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "caption": { "type": "STRING" },
                    "hashtags": {
                        "type": "ARRAY",
                        "items": { "type": "STRING" }
                    }
                },
                "required": ["caption", "hashtags"]
            }
        }
    }

    # Construct the API URL
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                api_url,
                headers=headers,
                json=payload
            )
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

            llm_response_data = response.json()

            # Check if candidates and content parts exist
            if (llm_response_data.get("candidates") and
                llm_response_data["candidates"][0].get("content") and
                llm_response_data["candidates"][0]["content"].get("parts") and
                llm_response_data["candidates"][0]["content"]["parts"][0].get("text")):

                content_string = llm_response_data["candidates"][0]["content"]["parts"][0]["text"]

                try:
                    # The response is already expected to be JSON due to responseSchema
                    parsed_content = json.loads(content_string)
                    return parsed_content
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from LLM: {e}")
                    print(f"Raw LLM content: {content_string}")
                    raise ValueError("LLM did not return valid JSON output as per schema.") from e
            else:
                print(f"Unexpected LLM response structure: {llm_response_data}")
                raise ValueError("LLM response missing expected content.")

        except httpx.HTTPStatusError as e:
            # Handle HTTP errors from the API
            error_message = f"Gemini API error: {e.response.status_code} - {e.response.text}"
            print(error_message)
            raise RuntimeError(error_message) from e
        except httpx.RequestError as e:
            # Handle network errors (e.g., connection refused, DNS error)
            error_message = f"Network error during Gemini API call: {e}"
            print(error_message)
            raise RuntimeError(error_message) from e
        except ValueError as ve:
            # Re-raise ValueError from JSON decoding or unexpected response structure
            raise ve
        except Exception as e:
            # Catch any other unexpected errors
            error_message = f"An unexpected error occurred during Gemini API call: {e}"
            print(error_message)
            raise RuntimeError(error_message) from e


def build_prompt_for_platform(data: CaptionInput, platform: str) -> str:
    """
    Builds a detailed prompt for the LLM to generate a social media caption
    for a specific platform, explicitly requesting JSON output.
    """
    tone_instruction = {
        "instagram": "The caption should be short, casual, fun, and emoji-rich. Include trendy hashtags.",
        "facebook": "The caption should be friendly, slightly longer, and include a strong CTA.",
        "linkedin": "The caption should be professional, insightful, and avoid slang or excessive emojis.",
    }.get(platform.lower(), "")

    return f"""
You are a social media expert creating a post for the {platform} platform.

Business Type: {data.business_type}
Post Description: {data.post_description}
Post Topic: {data.post_topic or 'N/A'}
Post Type: {data.post_type or 'N/A'}
Season: {data.season}
Location: {data.location or 'N/A'}

Instructions:
- Generate a 2–3 line caption for {platform}.
- Tailor it to the post topic and post type (e.g., reel, photo, carousel).
- Reflect the season and location.
- Encourage engagement or foot traffic.
- {tone_instruction}
- Include 5–8 niche-relevant hashtags (avoid generic ones like #love).

Output your response as a JSON object with two keys: "caption" (string) and "hashtags" (array of strings).
"""