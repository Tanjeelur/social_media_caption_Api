# # Gemini
# import os
# import httpx
# import json
# from typing import Optional, List, Dict, Any
# from pydantic import BaseModel
# from app.core.config import GEMINI_API_KEY, GEMINI_MODEL
# from app.models.captions import CaptionInput,EditRequest

# GEMINI_API_KEY =GEMINI_API_KEY
# #print(GEMINI_API_KEY)

# # Define the Gemini model to use
# GEMINI_MODEL = "gemini-2.0-flash" # Or another appropriate Gemini model

# async def call_gemini_api(prompt: str) -> dict:
#     """
#     Calls the Gemini API to generate content based on the provided prompt.
#     Expects and enforces JSON output from the LLM.
#     """
#     # Headers for Gemini API - Content-Type is important for structured responses
#     headers = {
#         "Content-Type": "application/json"
#     }

#     # The payload for the Gemini API call
#     payload = {
#         "contents": [
#             {
#                 "role": "user",
#                 "parts": [{"text": prompt}]
#             }
#         ],
#         "generationConfig": {
#             "responseMimeType": "application/json",
#             "responseSchema": {
#                 "type": "OBJECT",
#                 "properties": {
#                     "caption": { "type": "STRING" },
#                     "hashtags": {
#                         "type": "ARRAY",
#                         "items": { "type": "STRING" }
#                     }
#                 },
#                 "required": ["caption", "hashtags"]
#             }
#         }
#     }

#     # Construct the API URL
#     api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.post(
#                 api_url,
#                 headers=headers,
#                 json=payload
#             )
#             response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

#             llm_response_data = response.json()

#             # Check if candidates and content parts exist
#             if (llm_response_data.get("candidates") and
#                 llm_response_data["candidates"][0].get("content") and
#                 llm_response_data["candidates"][0]["content"].get("parts") and
#                 llm_response_data["candidates"][0]["content"]["parts"][0].get("text")):

#                 content_string = llm_response_data["candidates"][0]["content"]["parts"][0]["text"]

#                 try:
#                     # The response is already expected to be JSON due to responseSchema
#                     parsed_content = json.loads(content_string)
#                     return parsed_content
#                 except json.JSONDecodeError as e:
#                     print(f"Error decoding JSON from LLM: {e}")
#                     print(f"Raw LLM content: {content_string}")
#                     raise ValueError("LLM did not return valid JSON output as per schema.") from e
#             else:
#                 print(f"Unexpected LLM response structure: {llm_response_data}")
#                 raise ValueError("LLM response missing expected content.")

#         except httpx.HTTPStatusError as e:
#             # Handle HTTP errors from the API
#             error_message = f"Gemini API error: {e.response.status_code} - {e.response.text}"
#             print(error_message)
#             raise RuntimeError(error_message) from e
#         except httpx.RequestError as e:
#             # Handle network errors (e.g., connection refused, DNS error)
#             error_message = f"Network error during Gemini API call: {e}"
#             print(error_message)
#             raise RuntimeError(error_message) from e
#         except ValueError as ve:
#             # Re-raise ValueError from JSON decoding or unexpected response structure
#             raise ve
#         except Exception as e:
#             # Catch any other unexpected errors
#             error_message = f"An unexpected error occurred during Gemini API call: {e}"
#             print(error_message)
#             raise RuntimeError(error_message) from e




# openai_integration.py
import os
import openai
import json
from typing import Dict
from app.core.config import OPENAI_API_KEY  # You should add this to your config
from app.models.captions import CaptionInput,EditRequest
from openai import AsyncOpenAI
from openai._exceptions import AuthenticationError, RateLimitError, APIConnectionError, APIError



import httpx




async def call_openai_api(prompt: str):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a caption generator. Respond only in this JSON format:\n"
                    "{ \"caption\": \"your caption here\", \"hashtags\": [\"#tag1\", \"#tag2\"] }"
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )

    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]

    return json.loads(content)



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








def build_edit_prompt(edit_data: EditRequest) -> str:
    """
    Constructs a detailed prompt for the LLM to edit an existing caption.
    """
    prompt_parts = [
        f"Edit the following social media caption for {edit_data.platform}.",
        f"Original caption: \"\"\"{edit_data.original_caption}\"\"\"",
    ]
    edit_data.edit_type.lower()
    # Map edit_type to specific instructions
    if edit_data.edit_type == "rephrase":
        prompt_parts.append("Please rephrase the caption without changing its core meaning.")
    elif edit_data.edit_type == "shorten":
        prompt_parts.append("Please shorten the caption significantly while keeping it concise and engaging.")
    elif edit_data.edit_type == "expand":
        prompt_parts.append("Please expand the caption, adding more enticing and relevant details.")
    elif edit_data.edit_type == "formal":
        prompt_parts.append("Please rewrite the caption to be more formal and professional.")
    elif edit_data.edit_type == "casual":
        prompt_parts.append("Please rewrite the caption to be more casual, friendly, and relaxed.")
    elif edit_data.edit_type == "creative":
        prompt_parts.append("Please make the caption more creative, unique, and eye-catching.")
    else:
        prompt_parts.append("Perform a general improvement on the caption, making it more engaging.") # Fallback for unexpected edit_type or missing custom_instruction

    # Crucial for structured output from Gemini API with responseSchema
    prompt_parts.append("The output should be a JSON object with two keys: 'caption' (string) and 'hashtags' (array of strings).")
    prompt_parts.append("Keep the existing hashtags unless the instruction explicitly implies changing them (e.g., 'remove_hashtags').")
    prompt_parts.append("Example: {'caption': 'Your edited caption here.', 'hashtags': ['#editedtag1', '#editedtag2']}")

    return " ".join(prompt_parts).strip()
