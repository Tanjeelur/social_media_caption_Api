
# from fastapi import APIRouter, HTTPException
# from fastapi.responses import JSONResponse
# from app.models.captions import CaptionInput, EditRequest # Assuming this path is correct
# # from app.services.captions_service import build_prompt_for_platform,build_edit_prompt, call_gemini_api # Changed import
# from app.services.captions_service import build_prompt_for_platform,build_edit_prompt, call_openai_api # Updated import to include openai_call_api
# import re
# import httpx

# router = APIRouter()

# @router.post(
#     "/generate",
#     summary="Generate platform-specific captions and hashtags",
#     response_description="Generated caption and list of hashtags per platform",
# )
# async def generate_caption(input_data: CaptionInput):
#     """
#     Generates social media captions and hashtags for specified platforms
#     using the Gemini API.
#     """
#     results = {}

#     for platform in input_data.platforms:
#         try:
#             # Build the prompt for the specific platform
#             prompt = build_prompt_for_platform(input_data, platform)

#             # Call the LLM to get the generated caption and hashtags
#             # The LLM function is expected to return a dictionary
#             # with "caption" and "hashtags" keys due to responseSchema.
#             llm_output = await call_openai_api(prompt)

#             # Validate the structure of the LLM's output
#             if not isinstance(llm_output, dict) or "caption" not in llm_output or "hashtags" not in llm_output:
#                 raise ValueError("LLM returned an unexpected JSON structure. Expected 'caption' and 'hashtags' keys.")

#             # Extract raw caption and hashtags from the LLM's structured output
#             caption_raw = llm_output.get("caption", "").strip()
#             hashtags_from_llm_array = llm_output.get("hashtags", [])

#             extracted_hashtags = []
#             cleaned_caption_lines = []

#             # Process the caption to ensure no stray hashtags are left in the text
#             # (though with structured output, this step might be less critical,
#             # it's kept for robustness if the LLM occasionally includes them in the caption string)
#             for line in caption_raw.splitlines():
#                 found_tags = re.findall(r'#\w+', line)
#                 if found_tags:
#                     extracted_hashtags.extend(found_tags)
#                     cleaned_line = line
#                     for tag in found_tags:
#                         cleaned_line = cleaned_line.replace(tag, "").strip()
#                     if cleaned_line:
#                         cleaned_caption_lines.append(cleaned_line)
#                 else:
#                     cleaned_caption_lines.append(line)

#             caption = "\n".join(cleaned_caption_lines).strip()

#             # Clean and combine hashtags from both sources (extracted from caption and directly from LLM array)
#             valid_llm_array_hashtags = [
#                 tag.strip() for tag in hashtags_from_llm_array
#                 if isinstance(tag, str) and tag.startswith("#") # Ensure it's a string and starts with #
#             ]

#             all_hashtags = extracted_hashtags + valid_llm_array_hashtags
#             # Convert to lowercase and remove duplicates, then sort
#             hashtags_final = sorted(list(set(tag.lower() for tag in all_hashtags)))

#             # Store the results for the current platform
#             results[platform.lower()] = {
#                 "caption": caption,
#                 "hashtags": hashtags_final
#             }

#         except ValueError as ve:
#             # Handle errors related to LLM output processing (e.g., invalid JSON structure)
#             results[platform.lower()] = {
#                 "error": f"LLM processing error: {ve}"
#             }
#             # Log the error for debugging
#             print(f"Error processing LLM output for {platform}: {ve}")
#         except httpx.HTTPStatusError as e:
#             # Handle HTTP errors from the Gemini API (e.g., 400, 500 status codes)
#             results[platform.lower()] = {
#                 "error": f"Gemini API error: {e.response.status_code} - {e.response.text}" # Updated error message
#             }
#             # Log the error for debugging
#             print(f"Gemini API HTTP error for {platform}: {e.response.status_code} - {e.response.text}")
#         except httpx.RequestError as e:
#             # Handle network-related errors during the API call
#             results[platform.lower()] = {
#                 "error": f"Network error during API call: {e}"
#             }
#             # Log the error for debugging
#             print(f"Network error for {platform}: {e}")
#         except Exception as e:
#             # Catch any other unexpected errors
#             results[platform.lower()] = {
#                 "error": f"An unexpected internal server error occurred: {e}"
#             }
#             # Log the error for debugging
#             print(f"Unexpected error for {platform}: {e}")

#     # Return the aggregated results as a JSON response
#     return JSONResponse(content=results)


from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional, Union
from fastapi import Form
import json
import re
import httpx
import os


from app.models.captions import CaptionInput, EditRequest
from app.services.captions_service import (
    build_prompt_for_platform,
    call_openai_api,
    build_edit_prompt,
)

router = APIRouter()

@router.post("/generate", summary="Generate platform-specific captions and hashtags")
async def generate_caption(
    platforms: List[str] = Form(...),  # Accept as JSON string from Swagger
    post_type: str = Form(None),
    post_topic: str = Form(None),
    image: Union[UploadFile, str] = File(None)  # Accept image as UploadFile or empty string
    
):


    # Build input
    input_data = CaptionInput(
        platforms=platforms,
        post_type=post_type,
        post_topic=post_topic,
    )

    # Handle optional image
    if isinstance(image, str) or image is None or image == "":
        image_bytes = None
    else:
        image_bytes = await image.read()

    results = {}
    for platform in input_data.platforms:
        try:
            prompt = build_prompt_for_platform(input_data, platform, image_bytes=image_bytes)
            llm_output = await call_openai_api(prompt)
            results[platform.lower()] = llm_output
        except Exception as e:
            results[platform.lower()] = {"error": str(e)}

    return JSONResponse(content=results)


@router.post(
    "/edit",
    summary="Edit an existing caption", # Updated summary
    response_description="Edited caption", # Updated description
)
async def edit_caption(edit_data: EditRequest):
    """
    Edits an existing social media caption based on provided instructions
    using the Gemini API. Only the edited caption is returned.
    """
    
    try:
        prompt = build_edit_prompt(edit_data)
        llm_output = await call_openai_api(prompt)

        if not isinstance(llm_output, dict) or "caption" not in llm_output or "hashtags" not in llm_output:
            raise ValueError("LLM returned an unexpected JSON structure. Expected 'caption' and 'hashtags' keys.")

        caption_raw = llm_output.get("caption", "").strip()

        # Process the caption to ensure no stray hashtags are left in the text
        # (This logic is still useful even if we don't return hashtags,
        # as it cleans the caption itself)
        cleaned_caption_lines = []

        for line in caption_raw.splitlines():
            # Remove any hashtags embedded directly in the caption text
            cleaned_line = re.sub(r'#\w+', '', line).strip()
            if cleaned_line:
                cleaned_caption_lines.append(cleaned_line)

        caption = "\n".join(cleaned_caption_lines).strip()

        # --- IMPORTANT CHANGE HERE ---
        # Only return the caption, completely omitting the 'hashtags' field
        return JSONResponse(content={
            "caption": caption
        })

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"LLM processing error: {ve}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Gemini API error: {e.response.text}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Network error during API call: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected internal server error occurred: {e}")