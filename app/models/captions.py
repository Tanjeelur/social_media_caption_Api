from pydantic import BaseModel
from typing import Optional, List 
from fastapi import  UploadFile, File

class CaptionInput(BaseModel):
    platforms: List[str]  =["facebook", "instagram", "linkedin"]
    post_type: Optional[str] = "Story",
    post_topic: Optional[str] = "Meal",
    # image: Optional[UploadFile] = File(None)
    


class EditRequest(BaseModel):
    platform: List[str]
    original_caption: str
    edit_type: str  # rephrase, shorten, expand, formal, casual, creative

# NEW: Model for the AI-generated caption output
class GeneratedCaptionOutput(BaseModel):
    caption: str
    hashtags: List[str]