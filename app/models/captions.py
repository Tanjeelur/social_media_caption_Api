from pydantic import BaseModel
from typing import Optional

class CaptionInput(BaseModel):
    business_type: str
    post_description: str
    season: str
    location: Optional[str] = None
