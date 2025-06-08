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
        print("\n" + "="*80)
        print("🧠 STEP 1: CONTEXT ANALYSIS NODE")
        print("="*80)
        print(f"📝 Campaign Message: {state.request.campaign_message}")
        print(f"👥 Target Audience: {state.request.target_audience}")
        print(f"🎭 Tone: {state.request.tone.value}")
        print(f"😀 Use Emojis: {state.request.use_emojis}")
        
        logger.info("Starting context analysis...")
        
        if not state.request:
            raise ValueError("No request found in state")
        
        try:
            print("\n🤖 Calling AI Service for context analysis...")
            print("⏳ Analyzing campaign context and generating initial ideas...")
            
            context = await self.ai_service.analyze_context(
                state.request.campaign_message,
                state.request.target_audience,
                state.request.tone.value
            )
            
            print("\n✅ CONTEXT ANALYSIS RESPONSE:")
            print("-" * 40)
            if "key_messages" in context:
                print(f"🎯 Key Messages: {context['key_messages']}")
            if "audience_insights" in context:
                print(f"👤 Audience Insights: {context['audience_insights']}")
            if "platform_strategies" in context:
                print(f"📱 Platform Strategies:")
                for platform, strategy in context['platform_strategies'].items():
                    print(f"   • {platform.upper()}: {strategy}")
            if "creative_directions" in context:
                print(f"💡 Creative Directions: {context['creative_directions']}")
            print("-" * 40)
            
            # Extract creative_ideas from the context
            creative_ideas = context.get("creative_directions", [])
            
            print(f"\n📋 Extracted Creative Ideas: {creative_ideas}")
            print("✅ Context analysis completed successfully!")
            
            return {
                "campaign_context": context,
                "creative_ideas": creative_ideas
            }
        except Exception as e:
            print(f"\n❌ CONTEXT ANALYSIS ERROR: {e}")
            logger.error(f"Context analysis failed: {e}")
            # Return default structures that match the expected types
            fallback_context = {
                "key_messages": ["Kampány üzenet"],
                "audience_insights": f"Célközönség: {state.request.target_audience}",
                "platform_strategies": {
                    "facebook": "Általános stratégia",
                    "instagram": "Vizuális tartalom", 
                    "linkedin": "Professzionális tartalom",
                    "x": "Rövid tartalom"
                },
                "creative_directions": ["Kreatív megközelítés"]
            }
            print(f"🔄 Using fallback context: {fallback_context}")
            return {
                "campaign_context": fallback_context,
                "creative_ideas": ["Kreatív megközelítés"]
            }
    
    async def _generate_posts_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node 2: Generate platform-specific posts."""
        print("\n" + "="*80)
        print("📝 STEP 2: GENERATE POSTS NODE")
        print("="*80)
        print("🎯 Using context analysis results to generate platform-specific posts...")
        
        logger.info("Generating platform posts...")
        
        try:
            print("\n🤖 Calling AI Service for post generation...")
            print("📱 Generating posts for: Facebook, Instagram, LinkedIn, X...")
            
            posts_data = await self.ai_service.generate_platform_posts(
                state.campaign_context,
                state.request.campaign_message,
                state.request.target_audience,
                state.request.tone.value,
                state.request.use_emojis
            )
            
            print("\n✅ RAW AI RESPONSE:")
            print("-" * 40)
            for platform, data in posts_data.items():
                print(f"📱 {platform.upper()}:")
                if isinstance(data, dict):
                    if "text" in data:
                        print(f"   Text: {data['text'][:100]}{'...' if len(data['text']) > 100 else ''}")
                    if "hashtags" in data:
                        print(f"   Hashtags: {data['hashtags']}")
                    if "image_suggestions" in data:
                        print(f"   Images: {data['image_suggestions']}")
                print()
            print("-" * 40)
            
            # Convert to structured format
            print("🔄 Converting to structured format...")
            generated_posts = self._convert_to_response_format(posts_data)
            
            print("\n📊 STRUCTURED POSTS:")
            print("-" * 40)
            print(f"📘 Facebook: {generated_posts.facebook.text[:80]}{'...' if len(generated_posts.facebook.text) > 80 else ''}")
            print(f"   Hashtags: {generated_posts.facebook.hashtags}")
            print(f"📷 Instagram: {generated_posts.instagram.text[:80]}{'...' if len(generated_posts.instagram.text) > 80 else ''}")
            print(f"   Hashtags: {generated_posts.instagram.hashtags}")
            print(f"   Images: {generated_posts.instagram.image_suggestions}")
            print(f"💼 LinkedIn: {generated_posts.linkedin.text[:80]}{'...' if len(generated_posts.linkedin.text) > 80 else ''}")
            print(f"   Hashtags: {generated_posts.linkedin.hashtags}")
            print(f"🐦 X: {generated_posts.x.text[:80]}{'...' if len(generated_posts.x.text) > 80 else ''}")
            print(f"   Hashtags: {generated_posts.x.hashtags}")
            print("-" * 40)
            print("✅ Post generation completed successfully!")
            
            return {
                "generated_posts": generated_posts
            }
        except Exception as e:
            print(f"\n❌ POST GENERATION ERROR: {e}")
            logger.error(f"Post generation failed: {e}")
            return {"generated_posts": None}
    
    async def _await_feedback_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node 3: Present posts and await user feedback."""
        print("\n" + "="*80)
        print("⏸️ STEP 3: AWAIT FEEDBACK NODE")
        print("="*80)
        print("🔄 Posts generated and ready for user review...")
        print("📋 Current workflow state:")
        print(f"   • Posts generated: {state.generated_posts is not None}")
        print(f"   • Iteration count: {state.iteration_count}")
        print(f"   • Max iterations: {state.max_iterations}")
        print("⏳ Waiting for user feedback...")
        
        logger.info("Awaiting user feedback...")
        
        # This node doesn't modify state, just signals readiness for feedback
        # The actual feedback will be injected externally via update_state
        return {"needs_refinement": False}  # Default to no refinement needed
    
    async def _refine_posts_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node 4: Refine posts based on feedback."""
        print("\n" + "="*80)
        print("🔧 STEP 4: REFINE POSTS NODE")
        print("="*80)
        print(f"📝 User Feedback Received: {state.user_feedback}")
        print(f"🔄 Iteration: {state.iteration_count + 1}/{state.max_iterations}")
        
        logger.info("Refining posts based on feedback...")
        
        if not state.user_feedback:
            print("⚠️ No feedback provided, using current posts...")
            return {"refined_posts": state.generated_posts}
        
        try:
            print("\n🤖 Calling AI Service for post refinement...")
            print("🎯 Applying user feedback to improve posts...")
            
            # Convert current posts back to dict format for AI service
            current_posts_dict = self._convert_from_response_format(state.generated_posts)
            
            print("\n📤 SENDING TO AI:")
            print(f"   Current posts: {len(str(current_posts_dict))} characters")
            print(f"   Feedback: {state.user_feedback}")
            
            refined_data = await self.ai_service.refine_posts(
                current_posts_dict,
                state.user_feedback
            )
            
            print("\n✅ REFINEMENT RESPONSE:")
            print("-" * 40)
            for platform, data in refined_data.items():
                print(f"📱 {platform.upper()} (refined):")
                if isinstance(data, dict):
                    if "text" in data:
                        print(f"   Text: {data['text'][:100]}{'...' if len(data['text']) > 100 else ''}")
                    if "hashtags" in data:
                        print(f"   Hashtags: {data['hashtags']}")
                    if "image_suggestions" in data:
                        print(f"   Images: {data['image_suggestions']}")
                print()
            print("-" * 40)
            
            refined_posts = self._convert_to_response_format(refined_data)
            
            print("✅ Post refinement completed successfully!")
            print(f"🔄 Next iteration count: {state.iteration_count + 1}")
            
            return {
                "refined_posts": refined_posts,
                "iteration_count": state.iteration_count + 1,
                "needs_refinement": False,
                "user_feedback": None  # Clear feedback after processing
            }
        except Exception as e:
            print(f"\n❌ REFINEMENT ERROR: {e}")
            logger.error(f"Post refinement failed: {e}")
            print("🔄 Using original posts due to error...")
            return {"refined_posts": state.generated_posts}
    
    async def _finalize_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node 5: Finalize and format output."""
        print("\n" + "="*80)
        print("🏁 STEP 5: FINALIZE NODE")
        print("="*80)
        print("📋 Preparing final output...")
        
        logger.info("Finalizing results...")
        
        final_posts = state.refined_posts or state.generated_posts
        
        if not final_posts:
            print("❌ No posts available for finalization!")
            return {"final_result": {"error": "No posts generated"}}
        
        print(f"✅ Using {'refined' if state.refined_posts else 'original'} posts for final output")
        print(f"📊 Total iterations performed: {state.iteration_count}")
        
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
        
        print("\n📄 FINAL JSON OUTPUT:")
        print("-" * 40)
        import json
        print(json.dumps(final_result, indent=2, ensure_ascii=False))
        print("-" * 40)
        print("🎉 Finalization completed successfully!")
        
        return {"final_result": final_result}
    
    def _should_refine(self, state: WorkflowState) -> str:
        """Conditional logic to determine if refinement is needed."""
        decision = "refine" if state.needs_refinement else "finalize"
        print(f"\n🤔 DECISION POINT: Should refine? {state.needs_refinement} -> {decision}")
        return decision
    
    def _check_iteration_limit(self, state: WorkflowState) -> str:
        """Check if we should continue refining or finalize."""
        if state.iteration_count >= state.max_iterations:
            decision = "finalize"
            print(f"\n🛑 ITERATION LIMIT REACHED: {state.iteration_count}/{state.max_iterations} -> {decision}")
        else:
            decision = "continue"
            print(f"\n🔄 CONTINUING: {state.iteration_count}/{state.max_iterations} -> {decision}")
        return decision
    
    def _convert_to_response_format(self, posts_data: Dict) -> SocialMediaResponse:
        """Convert AI service response to structured format."""
        print("\n🔄 Converting AI response to structured format...")
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
            
            response = SocialMediaResponse(
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
            print("✅ Conversion successful!")
            return response
        except Exception as e:
            print(f"❌ Conversion error: {e}")
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
        print("🔄 Converting structured format back to dict for AI service...")
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
        print("\n" + "🚀" + "="*78 + "🚀")
        print("🤖 STARTING COMPLETE WORKFLOW PROCESSING")
        print("🚀" + "="*78 + "🚀")
        
        initial_state = WorkflowState(request=request)
        
        try:
            # Run the workflow
            result = await self.workflow.ainvoke(initial_state)
            
            print("\n" + "✅" + "="*78 + "✅")
            print("🎉 WORKFLOW COMPLETED SUCCESSFULLY")
            print("✅" + "="*78 + "✅")
            
            return result.get("final_result", {"error": "No result generated"})
        except Exception as e:
            print(f"\n❌ WORKFLOW EXECUTION FAILED: {e}")
            logger.error(f"Workflow execution failed: {e}")
            return {"error": str(e)}
    
    async def process_with_feedback(self, request: SocialMediaRequest) -> 'WorkflowRunner':
        """Start workflow and return a runner for feedback interaction."""
        print("\n" + "🔄" + "="*78 + "🔄")
        print("🤖 STARTING INTERACTIVE WORKFLOW WITH FEEDBACK")
        print("🔄" + "="*78 + "🔄")
        return WorkflowRunner(self.workflow, request)

class WorkflowRunner:
    """Helper class to manage workflow state and feedback interaction."""
    
    def __init__(self, workflow, request: SocialMediaRequest):
        self.workflow = workflow
        self.state = WorkflowState(request=request)
        self.current_step = "context_analysis"
        print(f"🏗️ WorkflowRunner initialized for request: {request.campaign_message[:50]}...")
    
    async def run_until_feedback(self) -> Dict[str, Any]:
        """Run workflow until feedback is needed."""
        print("\n" + "⏯️" + "="*78 + "⏯️")
        print("🎬 RUNNING WORKFLOW UNTIL FEEDBACK NEEDED")
        print("⏯️" + "="*78 + "⏯️")
        
        try:
            # Execute until we need feedback
            config = {"configurable": {"thread_id": "main"}}
            print(f"🔧 Using config: {config}")
            
            result = await self.workflow.ainvoke(self.state, config=config)
            self.state = WorkflowState(**result)
            
            print(f"\n📊 WORKFLOW STATE AFTER EXECUTION:")
            print(f"   • Generated posts: {self.state.generated_posts is not None}")
            print(f"   • Campaign context: {self.state.campaign_context is not None}")
            print(f"   • Iteration count: {self.state.iteration_count}")
            print(f"   • Needs refinement: {self.state.needs_refinement}")
            
            if self.state.generated_posts:
                print("\n✅ Posts generated successfully - ready for feedback!")
                return {
                    "status": "awaiting_feedback",
                    "posts": self.state.generated_posts,
                    "context": self.state.campaign_context
                }
            else:
                print("\n❌ Failed to generate posts!")
                return {"status": "error", "message": "Failed to generate posts"}
        except Exception as e:
            print(f"\n❌ WORKFLOW EXECUTION ERROR: {e}")
            logger.error(f"Workflow execution failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def provide_feedback(self, feedback: str) -> Dict[str, Any]:
        """Provide feedback and continue workflow."""
        print("\n" + "💬" + "="*78 + "💬")
        print("📝 PROCESSING USER FEEDBACK")
        print("💬" + "="*78 + "💬")
        print(f"📩 Feedback received: {feedback}")
        
        try:
            # Update state with feedback
            print("🔄 Updating workflow state with feedback...")
            self.state.user_feedback = feedback
            self.state.needs_refinement = True
            
            print(f"📊 Updated state:")
            print(f"   • User feedback: {self.state.user_feedback[:50]}...")
            print(f"   • Needs refinement: {self.state.needs_refinement}")
            print(f"   • Current iteration: {self.state.iteration_count}")
            
            # Continue workflow
            config = {"configurable": {"thread_id": "main"}}
            print("🔄 Continuing workflow with feedback...")
            
            result = await self.workflow.ainvoke(self.state, config=config)
            self.state = WorkflowState(**result)
            
            print(f"\n📊 WORKFLOW STATE AFTER FEEDBACK:")
            print(f"   • Final result: {self.state.final_result is not None}")
            print(f"   • Refined posts: {self.state.refined_posts is not None}")
            print(f"   • Iteration count: {self.state.iteration_count}")
            print(f"   • Max iterations: {self.state.max_iterations}")
            
            if self.state.final_result:
                print("🏁 Workflow completed with final result!")
                return {
                    "status": "completed",
                    "result": self.state.final_result
                }
            elif self.state.refined_posts:
                can_continue = self.state.iteration_count < self.state.max_iterations
                print(f"🔄 Posts refined successfully! Can continue: {can_continue}")
                return {
                    "status": "refined",
                    "posts": self.state.refined_posts,
                    "can_provide_more_feedback": can_continue
                }
            else:
                print("❌ Failed to process feedback!")
                return {"status": "error", "message": "Failed to process feedback"}
        except Exception as e:
            print(f"\n❌ FEEDBACK PROCESSING ERROR: {e}")
            logger.error(f"Feedback processing failed: {e}")
            return {"status": "error", "message": str(e)}