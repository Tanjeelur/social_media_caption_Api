# from fastapi import APIRouter, Request
# from fastapi.responses import JSONResponse
# from app.models.captions import CaptionInput
# from app.services.captions_service import build_prompt, call_openrouter

# router = APIRouter()

# @router.api_route("/generate", methods=["GET", "POST"])
# async def generate_caption(request: Request):
#     try:
#         # Parse input
#         if request.method == "GET":
#             params = dict(request.query_params)
#         else:
#             body = await request.json()
#             params = body if isinstance(body, dict) else {}

#         input_data = CaptionInput(**params)
#         prompt = build_prompt(input_data)
#         result = await call_openrouter(prompt)

#         # Extract caption and hashtags
#         if "hashtags" in result.lower():
#             parts = result.strip().split("\n\n")
#             caption = parts[0].strip()
#             hashtags = [line.strip("- ").strip() for line in parts[-1].splitlines() if "#" in line]
#         else:
#             caption = result.strip()
#             hashtags = []

#         return JSONResponse(content={"caption": caption, "hashtags": hashtags})
#     except Exception as e:
#         return JSONResponse(status_code=400, content={"error": str(e)})




# from fastapi import APIRouter
# from fastapi.responses import JSONResponse
# from app.models.captions import CaptionInput
# from app.services.captions_service import build_prompt, call_openrouter

# router = APIRouter()

# @router.post(
#     "/generate",
#     summary="Generate social media caption and hashtags",
#     response_description="Generated caption and list of hashtags",
# )
# async def generate_caption(input_data: CaptionInput):
#     try:
#         prompt = build_prompt(input_data)
#         result = await call_openrouter(prompt)

#         if "hashtags" in result.lower():
#             parts = result.strip().split("\n\n")
#             caption_text = parts[0].strip()
#             hashtag_lines = [line.strip("- ").strip() for line in parts[-1].splitlines() if "#" in line]
#             hashtags = [tag for tag in hashtag_lines if tag.startswith("#")]

#     # Remove entire lines from caption_text that contain any hashtags
#             lines = caption_text.splitlines()
#             clean_lines = [line for line in lines if not any(tag in line for tag in hashtags)]
#             caption = "\n".join(clean_lines).strip()
#         else:
#             caption = result.strip()
#             hashtags = []

#         return {"caption": caption, "hashtags": hashtags}
#     except Exception as e:
#         return JSONResponse(status_code=400, content={"error": str(e)})




# from fastapi import APIRouter, Request, Body
# from fastapi.responses import JSONResponse
# from app.models.captions import CaptionInput
# from app.services.captions_service import build_prompt, call_openrouter

# router = APIRouter()

# @router.api_route("/generate", methods=["GET", "POST"])
# async def generate_caption(
#     request: Request,
#     input_data: CaptionInput = Body(default=None)  # 👈 This line enables Swagger UI input
# ):
#     try:
#         # Support GET query input
#         if request.method == "GET":
#             params = dict(request.query_params)
#             input_data = CaptionInput(**params)  # Overwrite input_data with query version

#         prompt = build_prompt(input_data)
#         result = await call_openrouter(prompt)

#         # Extract caption and hashtags
#         if "hashtags" in result.lower():
#             parts = result.strip().split("\n\n")
#             caption = parts[0].strip()
#             hashtags = [line.strip("- ").strip() for line in parts[-1].splitlines() if "#" in line]
#         else:
#             caption = result.strip()
#             hashtags = []

#         return {"caption": caption, "hashtags": hashtags}
#     except Exception as e:
#         return JSONResponse(status_code=400, content={"error": str(e)})


from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.models.captions import CaptionInput
from app.services.captions_service import build_prompt, call_openrouter
import re # Import regex module

router = APIRouter()

@router.post(
    "/generate",
    summary="Generate social media caption and hashtags",
    response_description="Generated caption and list of hashtags",
)
async def generate_caption(input_data: CaptionInput):
    try:
        prompt = build_prompt(input_data)
        llm_output = await call_openrouter(prompt)

        # Basic validation of the dictionary structure returned by the LLM
        if not isinstance(llm_output, dict) or "caption" not in llm_output or "hashtags" not in llm_output:
            raise ValueError("LLM returned an unexpected JSON structure.")

        caption_raw = llm_output.get("caption", "").strip()
        hashtags_from_llm_array = llm_output.get("hashtags", [])

        extracted_hashtags = []
        cleaned_caption_lines = []

        # Step 1: Process the raw caption string
        # Iterate line by line to better handle cases where hashtags might be on separate lines
        lines = caption_raw.splitlines()
        for line in lines:
            # Find all hashtags in the current line
            found_tags = re.findall(r'#\w+', line) # Regex to find words starting with #
            if found_tags:
                extracted_hashtags.extend(found_tags)
                # Remove found hashtags from the line to clean the caption
                cleaned_line = line
                for tag in found_tags:
                    cleaned_line = cleaned_line.replace(tag, "").strip() # Remove the tag
                
                # Only add the cleaned line to the caption if it still has meaningful content
                if cleaned_line:
                    cleaned_caption_lines.append(cleaned_line)
            else:
                cleaned_caption_lines.append(line) # If no hashtags, add the line as is

        caption = "\n".join(cleaned_caption_lines).strip()
        
        # Step 2: Combine and deduplicate hashtags
        # Add hashtags from the LLM's array, if any, ensuring they start with '#'
        valid_llm_array_hashtags = [
            tag.strip() for tag in hashtags_from_llm_array
            if isinstance(tag, str) and tag.startswith("#")
        ]
        
        # Combine all extracted hashtags and those from the LLM's array
        all_hashtags = extracted_hashtags + valid_llm_array_hashtags
        
        # Remove duplicates and ensure lowercase (though prompt asks for lowercase, LLMs can deviate)
        # Using a set for deduplication, then convert back to list
        # We also convert to lowercase here to ensure consistency
        hashtags_final = sorted(list(set([tag.lower() for tag in all_hashtags])))


        return {"caption": caption, "hashtags": hashtags_final}

    except ValueError as ve:
        raise HTTPException(status_code=500, detail=f"LLM processing error: {ve}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"OpenRouter API error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")