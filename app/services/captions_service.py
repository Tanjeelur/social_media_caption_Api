
import os
import openai
import json
from typing import Dict, Optional, List
from app.core.config import OPENAI_API_KEY
from app.models.captions import CaptionInput, EditRequest
from openai import AsyncOpenAI
from openai._exceptions import AuthenticationError, RateLimitError, APIConnectionError, APIError

import httpx
import pprint

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
                    "You are a Social media caption generator. Respond only in this JSON format:\n"
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

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )

        response.raise_for_status() # This will raise an HTTPStatusError for 4xx/5xx responses
        llm_response_data = response.json()

        print("\n--- Raw LLM Response Data (from .json()) ---")
        pprint.pprint(llm_response_data)
        print("--- End Raw LLM Response Data ---\n")

        # Debugging the structure
        if "choices" not in llm_response_data:
            print("ERROR: 'choices' key not found in LLM response.")
            raise ValueError("LLM response missing 'choices' array.")

        if not isinstance(llm_response_data["choices"], list) or not llm_response_data["choices"]:
            print("ERROR: 'choices' is not a non-empty list.")
            raise ValueError("LLM response 'choices' is empty or not a list.")

        first_choice = llm_response_data["choices"][0]
        if "message" not in first_choice:
            print("ERROR: 'message' key not found in the first choice.")
            raise ValueError("LLM response choice missing 'message'.")

        message = first_choice["message"]
        if "content" not in message:
            print("ERROR: 'content' key not found in the message.")
            raise ValueError("LLM message missing 'content'.")

        content_string = message["content"]

        print(f"\n--- Extracted Content String ---\n{content_string}\n--- End Extracted Content String ---\n")

        try:
            parsed_content = json.loads(content_string)
            print(f"\n--- Successfully Parsed Content ---\n{parsed_content}\n--- End Successfully Parsed Content ---\n")
            return parsed_content
        except json.JSONDecodeError as e:
            print(f"ERROR: JSONDecodeError: {e}")
            print(f"Raw LLM content that failed to decode: '{content_string}'")
            raise ValueError("LLM did not return valid JSON output as per schema.") from e

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error during OpenAI API call: {e.response.status_code} - {e.response.text}")
        raise
    except httpx.RequestError as e:
        print(f"Network or request error during OpenAI API call: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise


def build_prompt_for_platform(data: CaptionInput, platform: str, image_bytes: Optional[bytes] = None ) -> str:
    """
    Builds a detailed prompt for the LLM to generate a social media caption
    for a specific platform, explicitly requesting JSON output.
    """
    tone_instruction = {
    "instagram": "The caption should be short, casual, fun, and emoji-rich. Include trendy hashtags.",
    "facebook": "The caption should be friendly, slightly longer, and include a strong CTA.",
    "linkedin": "The caption should be professional, insightful, and avoid slang or excessive emojis.",
    "twitter": "The caption should be punchy, witty, and under 280 characters. Use relevent emojis and hashtags.",
    "tiktok": "The caption should be catchy and aligned with trending sounds or challenges. Use playful language, emojis.",
    }.get(platform.lower(), "")

    return f"""
You are a social media expert creating a post for the {platform} platform.


Post Topic: {data.post_topic or 'N/A'}
Post Type: {data.post_type or 'N/A'}
Image: {'Provided' if image_bytes else 'Not provided'}

Instructions:
- Analyze the image (if provided) and the post topic. 
- Check relevant trends for {platform} on the basis of post topic and image.
- Generate a 2–3 line caption for {platform}.
- Tailor it to the post topic, image and post type (e.g.,post, reel, story).
- Encourage engagement or foot traffic.
- {tone_instruction}
- Include 5–8 niche-relevant hashtags (avoid generic ones like #love).

Output your response as a JSON object with two keys: "caption" (string) and "hashtags" (array of strings).
Reminder: This output must feel *native* to {platform}, not generic.
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
    elif edit_data.edit_type == "more formal":
        prompt_parts.append("Please rewrite the caption to be more formal and professional.")
    elif edit_data.edit_type == "more casual":
        prompt_parts.append("Please rewrite the caption to be more casual, friendly, and relaxed.")
    elif edit_data.edit_type == "more creative":
        prompt_parts.append("Please make the caption more creative, unique, and eye-catching.")
    else:
        prompt_parts.append("Perform a general improvement on the caption, making it more engaging.") # Fallback for unexpected edit_type or missing custom_instruction

    # Crucial for structured output from Gemini API with responseSchema
    prompt_parts.append("The output should be a JSON object with two keys: 'caption' (string) and 'hashtags' (array of strings).")
    prompt_parts.append("Keep the existing hashtags unless the instruction explicitly implies changing them (e.g., 'remove_hashtags').")
    prompt_parts.append("Example: {'caption': 'Your edited caption here.', 'hashtags': ['#editedtag1', '#editedtag2']}")

    return " ".join(prompt_parts).strip()
