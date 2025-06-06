from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from enum import Enum

class ToneType(str, Enum):
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    HUMOROUS = "humorous"
    CASUAL = "casual"
    FORMAL = "formal"

class SocialMediaRequest(BaseModel):
    campaign_message: str = Field(..., min_length=5, max_length=500, description="1-2 sentences describing the campaign")
    target_audience: str = Field(..., min_length=5, max_length=200, description="Brief description of target audience")
    tone: ToneType = Field(..., description="Tone of the posts")
    use_emojis: bool = Field(default=True, description="Whether to include emojis")

class PlatformPost(BaseModel):
    text: str
    hashtags: Optional[List[str]] = None
    image_suggestions: Optional[List[str]] = None

class SocialMediaResponse(BaseModel):
    facebook: PlatformPost
    instagram: PlatformPost
    linkedin: PlatformPost
    x: PlatformPost

class WorkflowState(BaseModel):
    # Input
    request: Optional[SocialMediaRequest] = None
    
    # Workflow state
    campaign_context: Optional[Dict[str, Any]] = None  # Changed from str to Dict
    creative_ideas: Optional[List[str]] = None  # Changed from Dict to List
    generated_posts: Optional[SocialMediaResponse] = None
    user_feedback: Optional[str] = None
    refined_posts: Optional[SocialMediaResponse] = None
    
    # Control flow
    needs_refinement: bool = False
    iteration_count: int = 0
    max_iterations: int = 3
    
    # Final output
    final_result: Optional[Dict] = None

class FeedbackRequest(BaseModel):
    feedback: str = Field(..., min_length=1, max_length=1000, description="User feedback for refinement")
    specific_platforms: Optional[List[str]] = Field(default=None, description="Specific platforms to focus on")