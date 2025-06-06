import streamlit as st
import asyncio
import json
import logging
from typing import Dict, Any, Optional
import os
import sys

# Add src directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules with absolute imports
from models.request_models import SocialMediaRequest, ToneType
from agents.social_media_agent import SocialMediaAgent, WorkflowRunner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI Social Media Agent",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🤖 AI Social Media Agent")
st.markdown("Generate optimized posts for multiple platforms with AI-powered feedback loop")

# Initialize session state
if 'workflow_runner' not in st.session_state:
    st.session_state.workflow_runner = None
if 'current_posts' not in st.session_state:
    st.session_state.current_posts = None
if 'workflow_status' not in st.session_state:
    st.session_state.workflow_status = "ready"
if 'context_analysis' not in st.session_state:
    st.session_state.context_analysis = None

def check_api_key():
    """Check if Groq or OpenAI API key is configured."""
    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    # Check for placeholder values (not real keys)
    if groq_key in ["YOUR_NEW_GROQ_API_KEY", "your_groq_api_key_here", None, ""]:
        groq_key = None
    if openai_key in ["your_openai_api_key_here", None, ""]:
        openai_key = None
    
    if not groq_key and not openai_key:
        st.error("⚠️ **API Key Required**")
        st.markdown("""
        **For Local Development:**
        1. Get a free API key from [Groq Console](https://console.groq.com/)
        2. Create a `.env` file in your project root
        3. Add: `GROQ_API_KEY=your_actual_key_here`
        
        **For Streamlit Cloud:**
        1. Go to your app settings
        2. Click "Secrets" in Advanced settings
        3. Add: `GROQ_API_KEY = "your_actual_key_here"`
        """)
        return False
    
    if groq_key:
        st.success("✅ Using Groq API")
    else:
        st.success("✅ Using OpenAI API")
    return True

async def run_workflow_until_feedback(agent: SocialMediaAgent, request: SocialMediaRequest):
    """Run the LangGraph workflow until feedback is needed."""
    try:
        runner = await agent.process_with_feedback(request)
        result = await runner.run_until_feedback()
        return runner, result
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        return None, {"status": "error", "message": str(e)}

async def provide_feedback_to_workflow(runner: WorkflowRunner, feedback: str):
    """Provide feedback to the workflow and get refined results."""
    try:
        result = await runner.provide_feedback(feedback)
        return result
    except Exception as e:
        logger.error(f"Feedback processing failed: {e}")
        return {"status": "error", "message": str(e)}

def display_posts(posts, title="Generated Posts"):
    """Display posts in a nice format."""
    st.subheader(title)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Facebook
        st.markdown("### 📘 Facebook")
        with st.container():
            st.write(posts.facebook.text)
            if posts.facebook.hashtags:
                st.write("**Hashtags:** " + " ".join([f"#{tag}" for tag in posts.facebook.hashtags]))
        
        # LinkedIn
        st.markdown("### 💼 LinkedIn")
        with st.container():
            st.write(posts.linkedin.text)
            if posts.linkedin.hashtags:
                st.write("**Hashtags:** " + " ".join([f"#{tag}" for tag in posts.linkedin.hashtags]))
    
    with col2:
        # Instagram
        st.markdown("### 📷 Instagram")
        with st.container():
            st.write(posts.instagram.text)
            if posts.instagram.hashtags:
                st.write("**Hashtags:** " + " ".join([f"#{tag}" for tag in posts.instagram.hashtags]))
            if posts.instagram.image_suggestions:
                st.write("**Image suggestions:**")
                for i, suggestion in enumerate(posts.instagram.image_suggestions, 1):
                    st.write(f"  {i}. {suggestion}")
        
        # X (Twitter)
        st.markdown("### 🐦 X (Twitter)")
        with st.container():
            st.write(posts.x.text)
            if posts.x.hashtags:
                st.write("**Hashtags:** " + " ".join([f"#{tag}" for tag in posts.x.hashtags]))

def display_context_analysis(context):
    """Display context analysis in sidebar."""
    if context and "error" not in context:
        with st.sidebar:
            st.markdown("### 🧠 Context Analysis")
            
            if "key_messages" in context:
                st.markdown("**Key Messages:**")
                for msg in context["key_messages"]:
                    st.write(f"• {msg}")
            
            if "audience_insights" in context:
                st.markdown("**Audience Insights:**")
                st.write(context["audience_insights"])
            
            if "creative_directions" in context:
                st.markdown("**Creative Directions:**")
                for direction in context["creative_directions"]:
                    st.write(f"• {direction}")

def main():
    """Main application logic."""
    
    # Check API key
    if not check_api_key():
        return
    
    # Sidebar for input
    with st.sidebar:
        st.header("📝 Campaign Details")
        
        # Input form
        with st.form("campaign_form"):
            campaign_message = st.text_area(
                "Campaign Message",
                placeholder="Enter your 1-2 sentence campaign message here...",
                help="Brief description of your campaign or product"
            )
            
            target_audience = st.text_input(
                "Target Audience",
                placeholder="e.g., 25-35 year old hobby gamers",
                help="Brief description of your target audience"
            )
            
            tone = st.selectbox(
                "Tone",
                options=[e.value for e in ToneType],
                help="Choose the tone for your posts"
            )
            
            use_emojis = st.checkbox(
                "Use Emojis",
                value=True,
                help="Include relevant emojis in posts"
            )
            
            submit_button = st.form_submit_button("🚀 Generate Posts")
        
        # Display context analysis if available
        if st.session_state.context_analysis:
            display_context_analysis(st.session_state.context_analysis)
    
    # Main content area
    if submit_button:
        if not campaign_message or not target_audience:
            st.error("Please fill in both campaign message and target audience.")
            return
        
        # Create request
        try:
            request = SocialMediaRequest(
                campaign_message=campaign_message,
                target_audience=target_audience,
                tone=ToneType(tone),
                use_emojis=use_emojis
            )
        except Exception as e:
            st.error(f"Invalid input: {e}")
            return
        
        # Show progress
        with st.spinner("🤖 AI is analyzing your campaign and generating posts..."):
            try:
                # Initialize agent and run workflow
                agent = SocialMediaAgent()
                
                # Run async workflow
                runner, result = asyncio.run(run_workflow_until_feedback(agent, request))
                
                if result["status"] == "awaiting_feedback":
                    st.session_state.workflow_runner = runner
                    st.session_state.current_posts = result["posts"]
                    st.session_state.workflow_status = "awaiting_feedback"
                    st.session_state.context_analysis = result.get("context")
                    st.success("✅ Posts generated successfully!")
                else:
                    st.error(f"Failed to generate posts: {result.get('message', 'Unknown error')}")
                    return
                    
            except Exception as e:
                st.error(f"Error: {e}")
                return
    
    # Display current posts if available
    if st.session_state.current_posts:
        display_posts(st.session_state.current_posts)
        
        # Feedback section
        if st.session_state.workflow_status == "awaiting_feedback":
            st.markdown("---")
            st.subheader("💬 Provide Feedback")
            st.markdown("Review the generated posts above and provide feedback for improvements:")
            
            feedback_text = st.text_area(
                "Your feedback",
                placeholder="e.g., Make the Facebook post more engaging, add more hashtags to Instagram, make LinkedIn more professional...",
                help="Describe what you'd like to change or improve in the posts"
            )
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("🔄 Refine Posts", type="primary"):
                    if feedback_text.strip():
                        with st.spinner("🤖 Refining posts based on your feedback..."):
                            try:
                                result = asyncio.run(provide_feedback_to_workflow(
                                    st.session_state.workflow_runner, 
                                    feedback_text
                                ))
                                
                                if result["status"] == "refined":
                                    st.session_state.current_posts = result["posts"]
                                    st.success("✅ Posts refined successfully!")
                                    if result.get("can_provide_more_feedback", False):
                                        st.info("You can provide more feedback if needed.")
                                    else:
                                        st.session_state.workflow_status = "completed"
                                        st.info("Maximum refinement iterations reached.")
                                elif result["status"] == "completed":
                                    st.session_state.workflow_status = "completed"
                                    st.success("✅ Final posts generated!")
                                    # Display final result
                                    st.json(result["result"])
                                else:
                                    st.error(f"Refinement failed: {result.get('message', 'Unknown error')}")
                            except Exception as e:
                                st.error(f"Error during refinement: {e}")
                    else:
                        st.warning("Please provide feedback before refining.")
            
            with col2:
                if st.button("✅ Finalize Posts"):
                    try:
                        # Get final result
                        result = asyncio.run(provide_feedback_to_workflow(
                            st.session_state.workflow_runner, 
                            "Finalize current posts"
                        ))
                        
                        st.session_state.workflow_status = "completed"
                        st.success("✅ Posts finalized!")
                        
                        # Show final JSON output
                        st.subheader("📄 Final Output (JSON)")
                        if "result" in result:
                            st.json(result["result"])
                        else:
                            # Convert current posts to final format
                            posts = st.session_state.current_posts
                            final_output = {
                                "facebook": {
                                    "text": posts.facebook.text,
                                    "hashtags": posts.facebook.hashtags or []
                                },
                                "instagram": {
                                    "text": posts.instagram.text,
                                    "hashtags": posts.instagram.hashtags or [],
                                    "image_suggestions": posts.instagram.image_suggestions or []
                                },
                                "linkedin": {
                                    "text": posts.linkedin.text,
                                    "hashtags": posts.linkedin.hashtags or []
                                },
                                "x": {
                                    "text": posts.x.text,
                                    "hashtags": posts.x.hashtags or []
                                }
                            }
                            st.json(final_output)
                            
                            # Download button
                            st.download_button(
                                label="📥 Download JSON",
                                data=json.dumps(final_output, indent=2, ensure_ascii=False),
                                file_name="social_media_posts.json",
                                mime="application/json"
                            )
                    except Exception as e:
                        st.error(f"Error finalizing posts: {e}")

if __name__ == "__main__":
    main()