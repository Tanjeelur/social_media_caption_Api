
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional, Union
import json
import re
import httpx
import os

from app.models.captions import CaptionInput, EditRequest
from app.services.captions_service import (
    build_prompt_for_platform,
    call_openai_api,
    build_edit_prompt,
    describe_image
)

router = APIRouter()

@router.post(
    "/caption",
    summary="Merged endpoint for generating or editing captions",
    response_description="Generated or edited caption based on edit_type parameter"
)
async def merged_caption_endpoint(
    platforms: List[str] = Form(...),
    post_type: Optional[str] = Form(None),
    post_topic: Optional[str] = Form(None),
    caption: Optional[str] = Form(None),
    edit_type: Optional[str] = Form(None),
    image: Union[UploadFile, str] = File(None)
):
    """
    Merged endpoint that handles both caption generation and editing.
    - If edit_type is empty → generate a new caption
    - If edit_type has a value → edit the existing caption
    """
    
    # # Handle optional image
    # if isinstance(image, str) or image is None or image == "":
    #     image_bytes = None
    # else:
    #     image_bytes = await image.read()

    # Define the temp folder
    TEMP_DIR = os.path.join(os.getcwd(), "temp_images")
    os.makedirs(TEMP_DIR, exist_ok=True)

    # Fixed filename for uploaded image
    IMAGE_FILENAME = "current_post_image.jpg"

    if image:
        image_path = os.path.join(TEMP_DIR, IMAGE_FILENAME)
        with open(image_path, "wb") as f:
            f.write(await image.read())
        
        # Generate description using the overwritten file
        description = describe_image(image_path)

        # Merge with post_topic
        if post_type and post_topic:
            post_topic = f"{post_type} {post_topic}. Image: {description}"
        elif post_type:
            post_topic = f"{post_type}. Image: {description}"
        elif post_topic:
            post_topic = f"{post_topic}. Image: {description}"
        else:
            post_topic = f"Image: {description}"

    # Logic: If edit_type is empty → generate a new caption
    if not edit_type or edit_type.strip() == "":
        # Generate new caption logic
        input_data = CaptionInput(
            platforms=platforms,
            post_type=post_type,
            post_topic=post_topic,
        )

        results = {}
        for platform in platforms:
            try:
                prompt = build_prompt_for_platform(input_data, platform)
                llm_output = await call_openai_api(prompt)
                results[platform.lower()] = llm_output
            except Exception as e:
                results[platform.lower()] = {"error": str(e)}

        return JSONResponse(content=results)
    
    # Logic: If edit_type has a value → edit the existing caption
    else:
        # Edit existing caption logic
        if not caption:
            raise HTTPException(status_code=400, detail="Caption is required when edit_type is provided")
        
        edit_data = EditRequest(
            platform=platforms,
            original_caption=caption,
            edit_type=edit_type
        )
        
        try:
            prompt = build_edit_prompt(edit_data)
            llm_output = await call_openai_api(prompt)

            if not isinstance(llm_output, dict) or "caption" not in llm_output or "hashtags" not in llm_output:
                raise ValueError("LLM returned an unexpected JSON structure. Expected 'caption' and 'hashtags' keys.")

            caption_raw = llm_output.get("caption", "").strip()

            # Process the caption to ensure no stray hashtags are left in the text
            cleaned_caption_lines = []

            for line in caption_raw.splitlines():
                # Remove any hashtags embedded directly in the caption text
                cleaned_line = re.sub(r'#\w+', '', line).strip()
                if cleaned_line:
                    cleaned_caption_lines.append(cleaned_line)

            edited_caption = "\n".join(cleaned_caption_lines).strip()

            return JSONResponse(content={
                "caption": edited_caption
            })

        except ValueError as ve:
            raise HTTPException(status_code=400, detail=f"LLM processing error: {ve}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"OpenAI API error: {e.response.text}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Network error during API call: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected internal server error occurred: {e}")