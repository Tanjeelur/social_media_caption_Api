from pydantic import BaseModel
from typing import Optional, List

class CaptionInput(BaseModel):

    business_type: Optional[str] = None 
    post_description: Optional[str] = None 
    season: Optional[str] = None 
    location: Optional[str] = None
    platforms: List[str]  # facebook, instagram, linkedin
    post_topic: Optional[str] = None  # e.g. "customer spotlight"
    post_type: Optional[str] = None  