from pydantic import BaseModel
from typing import Optional, List

class CaptionInput(BaseModel):

    business_type: Optional[str] = "Restaurant" 
    post_description: Optional[str] = "A couple having dinner" 
    season: Optional[str] = "Spring" 
    location: Optional[str] = "Spain"
    platforms: List[str]  =["facebook", "instagram", "linkedin"]# facebook, instagram, linkedin
    post_topic: Optional[str] = "Meal"  # e.g. "customer spotlight"
    post_type: Optional[str] = "Story" 


class EditRequest(BaseModel):
    platform: List[str]
    original_caption: str
    edit_type: str  # rephrase, shorten, expand, formal, casual, creative