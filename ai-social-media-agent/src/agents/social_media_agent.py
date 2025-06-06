from langgraph.graph import StateGraph, END
from typing import Dict, Any
import asyncio
import logging
from models.request_models import WorkflowState, SocialMediaRequest, SocialMediaResponse, PlatformPost
from services.ai_service import AIService

logger = logging.getLogger(__name__)

class SocialMediaAgent:
    def __init__(self):
        self.ai_service = AIService()
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow with all nodes and edges."""
        
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("context_analysis", self._context_analysis_node)
        workflow.add_node("generate_posts", self._generate_posts_node)
        workflow.add_node("await_feedback", self._await_feedback_node)
        workflow.add_node("refine_posts", self._refine_posts_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Add edges
        workflow.set_entry_point("context_analysis")
        workflow.add_edge("context_analysis", "generate_posts")
        workflow.add_edge("generate_posts", "await_feedback")
        
        # Conditional edge for feedback processing
        workflow.add_conditional_edges(
            "await_feedback",
            self._should_refine,
            {
                "refine": "refine_posts",
                "finalize": "finalize"
            }
        )
        
        workflow.add_conditional_edges(
            "refine_posts",
            self._check_iteration_limit,
            {
                "continue": "await_feedback",
                "finalize": "finalize"
            }
        )
        
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    async def _context_analysis_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node 1: Analyze campaign context and generate initial ideas."""
        logger.info("Starting context analysis...")
        
        if not state.request:
            raise ValueError("No request found in state")
        
        try:
            context = await self.ai_service.analyze_context(
                state.request.campaign_message,
                state.request.target_audience,
                state.request.tone.value
            )
            
            # Extract creative_ideas from the context
            creative_ideas = context.get("creative_directions", [])
            
            return {
                "campaign_context": context,
                "creative_ideas": creative_ideas
            }
        except Exception as e:
            logger.error(f"Context analysis failed: {e}")
            # Return default structures that match the expected types
            return {
                "campaign_context": {
                    "key_messages": ["Kampány üzenet"],
                    "audience_insights": f"Célközönség: {state.request.target_audience}",
                    "platform_strategies": {
                        "facebook": "Általános stratégia",
                        "instagram": "Vizuális tartalom", 
                        "linkedin": "Professzionális tartalom",
                        "x": "Rövid tartalom"
                    },
                    "creative_directions": ["Kreatív megközelítés"]
                },
                "creative_ideas": ["Kreatív megközelítés"]
            }
    
    async def _generate_posts_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node 2: Generate platform-specific posts."""
        logger.info("Generating platform posts...")
        
        try:
            posts_data = await self.ai_service.generate_platform_posts(
                state.campaign_context,
                state.request.campaign_message,
                state.request.target_audience,
                state.request.tone.value,
                state.request.use_emojis
            )
            
            # Convert to structured format
            generated_posts = self._convert_to_response_format(posts_data)
            
            return {
                "generated_posts": generated_posts
            }
        except Exception as e:
            logger.error(f"Post generation failed: {e}")
            return {"generated_posts": None}
    
    async def _await_feedback_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node 3: Present posts and await user feedback."""
        logger.info("Awaiting user feedback...")
        
        # This node doesn't modify state, just signals readiness for feedback
        # The actual feedback will be injected externally via update_state
        return {"needs_refinement": False}  # Default to no refinement needed
    
    async def _refine_posts_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node 4: Refine posts based on feedback."""
        logger.info("Refining posts based on feedback...")
        
        if not state.user_feedback:
            return {"refined_posts": state.generated_posts}
        
        try:
            # Convert current posts back to dict format for AI service
            current_posts_dict = self._convert_from_response_format(state.generated_posts)
            
            refined_data = await self.ai_service.refine_posts(
                current_posts_dict,
                state.user_feedback
            )
            
            refined_posts = self._convert_to_response_format(refined_data)
            
            return {
                "refined_posts": refined_posts,
                "iteration_count": state.iteration_count + 1,
                "needs_refinement": False,
                "user_feedback": None  # Clear feedback after processing
            }
        except Exception as e:
            logger.error(f"Post refinement failed: {e}")
            return {"refined_posts": state.generated_posts}
    
    async def _finalize_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node 5: Finalize and format output."""
        logger.info("Finalizing results...")
        
        final_posts = state.refined_posts or state.generated_posts
        
        if not final_posts:
            return {"final_result": {"error": "No posts generated"}}
        
        # Convert to final JSON format
        final_result = {
            "facebook": {
                "text": final_posts.facebook.text,
                "hashtags": final_posts.facebook.hashtags or []
            },
            "instagram": {
                "text": final_posts.instagram.text,
                "hashtags": final_posts.instagram.hashtags or [],
                "image_suggestions": final_posts.instagram.image_suggestions or []
            },
            "linkedin": {
                "text": final_posts.linkedin.text,
                "hashtags": final_posts.linkedin.hashtags or []
            },
            "x": {
                "text": final_posts.x.text,
                "hashtags": final_posts.x.hashtags or []
            }
        }
        
        return {"final_result": final_result}
    
    def _should_refine(self, state: WorkflowState) -> str:
        """Conditional logic to determine if refinement is needed."""
        return "refine" if state.needs_refinement else "finalize"
    
    def _check_iteration_limit(self, state: WorkflowState) -> str:
        """Check if we should continue refining or finalize."""
        if state.iteration_count >= state.max_iterations:
            return "finalize"
        return "continue"
    
    def _convert_to_response_format(self, posts_data: Dict) -> SocialMediaResponse:
        """Convert AI service response to structured format."""
        try:
            # Handle both variation format and direct format
            facebook_data = posts_data.get("facebook", {})
            if "variation_1" in facebook_data:
                facebook_data = facebook_data["variation_1"]  # Use first variation
            
            instagram_data = posts_data.get("instagram", {})
            if "variation_1" in instagram_data:
                instagram_data = instagram_data["variation_1"]
            
            linkedin_data = posts_data.get("linkedin", {})
            if "variation_1" in linkedin_data:
                linkedin_data = linkedin_data["variation_1"]
            
            x_data = posts_data.get("x", {})
            if "variation_1" in x_data:
                x_data = x_data["variation_1"]
            
            return SocialMediaResponse(
                facebook=PlatformPost(
                    text=facebook_data.get("text", ""),
                    hashtags=facebook_data.get("hashtags", [])
                ),
                instagram=PlatformPost(
                    text=instagram_data.get("text", ""),
                    hashtags=instagram_data.get("hashtags", []),
                    image_suggestions=instagram_data.get("image_suggestions", [])
                ),
                linkedin=PlatformPost(
                    text=linkedin_data.get("text", ""),
                    hashtags=linkedin_data.get("hashtags", [])
                ),
                x=PlatformPost(
                    text=x_data.get("text", ""),
                    hashtags=x_data.get("hashtags", [])
                )
            )
        except Exception as e:
            logger.error(f"Error converting to response format: {e}")
            # Return empty response on error
            return SocialMediaResponse(
                facebook=PlatformPost(text="Error generating content"),
                instagram=PlatformPost(text="Error generating content"),
                linkedin=PlatformPost(text="Error generating content"),
                x=PlatformPost(text="Error generating content")
            )
    
    def _convert_from_response_format(self, response: SocialMediaResponse) -> Dict:
        """Convert structured format back to dict for AI service."""
        return {
            "facebook": {
                "text": response.facebook.text,
                "hashtags": response.facebook.hashtags or []
            },
            "instagram": {
                "text": response.instagram.text,
                "hashtags": response.instagram.hashtags or [],
                "image_suggestions": response.instagram.image_suggestions or []
            },
            "linkedin": {
                "text": response.linkedin.text,
                "hashtags": response.linkedin.hashtags or []
            },
            "x": {
                "text": response.x.text,
                "hashtags": response.x.hashtags or []
            }
        }
    
    async def process_request(self, request: SocialMediaRequest) -> Dict[str, Any]:
        """Process a complete request through the workflow."""
        initial_state = WorkflowState(request=request)
        
        try:
            # Run the workflow
            result = await self.workflow.ainvoke(initial_state)
            return result.get("final_result", {"error": "No result generated"})
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {"error": str(e)}
    
    async def process_with_feedback(self, request: SocialMediaRequest) -> 'WorkflowRunner':
        """Start workflow and return a runner for feedback interaction."""
        return WorkflowRunner(self.workflow, request)

class WorkflowRunner:
    """Helper class to manage workflow state and feedback interaction."""
    
    def __init__(self, workflow, request: SocialMediaRequest):
        self.workflow = workflow
        self.state = WorkflowState(request=request)
        self.current_step = "context_analysis"
    
    async def run_until_feedback(self) -> Dict[str, Any]:
        """Run workflow until feedback is needed."""
        try:
            # Execute until we need feedback
            config = {"configurable": {"thread_id": "main"}}
            result = await self.workflow.ainvoke(self.state, config=config)
            self.state = WorkflowState(**result)
            
            if self.state.generated_posts:
                return {
                    "status": "awaiting_feedback",
                    "posts": self.state.generated_posts,
                    "context": self.state.campaign_context
                }
            else:
                return {"status": "error", "message": "Failed to generate posts"}
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def provide_feedback(self, feedback: str) -> Dict[str, Any]:
        """Provide feedback and continue workflow."""
        try:
            # Update state with feedback
            self.state.user_feedback = feedback
            self.state.needs_refinement = True
            
            # Continue workflow
            config = {"configurable": {"thread_id": "main"}}
            result = await self.workflow.ainvoke(self.state, config=config)
            self.state = WorkflowState(**result)
            
            if self.state.final_result:
                return {
                    "status": "completed",
                    "result": self.state.final_result
                }
            elif self.state.refined_posts:
                return {
                    "status": "refined",
                    "posts": self.state.refined_posts,
                    "can_provide_more_feedback": self.state.iteration_count < self.state.max_iterations
                }
            else:
                return {"status": "error", "message": "Failed to process feedback"}
        except Exception as e:
            logger.error(f"Feedback processing failed: {e}")
            return {"status": "error", "message": str(e)}