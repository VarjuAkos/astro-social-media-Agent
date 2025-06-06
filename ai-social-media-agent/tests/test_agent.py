import pytest
import asyncio
from unittest.mock import Mock, patch
from src.models.request_models import SocialMediaRequest, ToneType, WorkflowState
from src.agents.social_media_agent import SocialMediaAgent

class TestSocialMediaAgent:
    
    @pytest.fixture
    def sample_request(self):
        return SocialMediaRequest(
            campaign_message="Új gaming laptop kollekciónk most 20% kedvezménnyel kapható!",
            target_audience="25-35 éves hobby gamerek",
            tone=ToneType.FRIENDLY,
            use_emojis=True
        )
    
    @pytest.fixture
    def mock_ai_response(self):
        return {
            "facebook": {
                "variation_1": {
                    "text": "Test Facebook post",
                    "hashtags": ["#gaming", "#laptop"]
                }
            },
            "instagram": {
                "variation_1": {
                    "text": "Test Instagram post",
                    "hashtags": ["#gaming"],
                    "image_suggestions": ["Gaming setup", "Laptop closeup"]
                }
            },
            "linkedin": {
                "variation_1": {
                    "text": "Professional LinkedIn post",
                    "hashtags": ["#technology"]
                }
            },
            "x": {
                "variation_1": {
                    "text": "Short X post",
                    "hashtags": ["#gaming"]
                }
            }
        }
    
    def test_workflow_state_initialization(self):
        """Test that WorkflowState initializes correctly."""
        state = WorkflowState()
        assert state.iteration_count == 0
        assert state.max_iterations == 3
        assert state.needs_refinement == False
        assert state.final_result is None
    
    @patch('src.services.ai_service.AIService.analyze_context')
    async def test_context_analysis_node(self, mock_analyze, sample_request):
        """Test the context analysis node."""
        agent = SocialMediaAgent()
        
        mock_context = {
            "key_messages": ["Gaming laptops on sale"],
            "audience_insights": "Tech-savvy gamers aged 25-35",
            "creative_directions": ["Performance focus", "Value proposition"]
        }
        mock_analyze.return_value = mock_context
        
        state = WorkflowState(request=sample_request)
        result = await agent._context_analysis_node(state)
        
        assert "context_analysis" in result
        assert result["context_analysis"] == mock_context
        mock_analyze.assert_called_once()
    
    @patch('src.services.ai_service.AIService.generate_platform_posts')
    async def test_generate_posts_node(self, mock_generate, sample_request, mock_ai_response):
        """Test the post generation node."""
        agent = SocialMediaAgent()
        mock_generate.return_value = mock_ai_response
        
        state = WorkflowState(
            request=sample_request,
            context_analysis={"key_messages": ["test"]}
        )
        
        result = await agent._generate_posts_node(state)
        
        assert "generated_posts" in result
        assert result["generated_posts"] is not None
        mock_generate.assert_called_once()
    
    def test_convert_to_response_format(self, mock_ai_response):
        """Test conversion from AI response to structured format."""
        agent = SocialMediaAgent()
        response = agent._convert_to_response_format(mock_ai_response)
        
        assert response.facebook.text == "Test Facebook post"
        assert response.instagram.text == "Test Instagram post"
        assert response.linkedin.text == "Professional LinkedIn post"
        assert response.x.text == "Short X post"
        
        assert len(response.instagram.image_suggestions) == 2
        assert "Gaming setup" in response.instagram.image_suggestions
    
    def test_should_refine_logic(self, sample_request):
        """Test refinement decision logic."""
        agent = SocialMediaAgent()
        
        # Test no refinement needed
        state_no_refine = WorkflowState(needs_refinement=False)
        assert agent._should_refine(state_no_refine) == "finalize"
        
        # Test refinement needed
        state_refine = WorkflowState(needs_refinement=True)
        assert agent._should_refine(state_refine) == "refine"
    
    def test_iteration_limit_check(self, sample_request):
        """Test iteration limit checking."""
        agent = SocialMediaAgent()
        
        # Test under limit
        state_under = WorkflowState(iteration_count=1, max_iterations=3)
        assert agent._check_iteration_limit(state_under) == "continue"
        
        # Test at limit
        state_at_limit = WorkflowState(iteration_count=3, max_iterations=3)
        assert agent._check_iteration_limit(state_at_limit) == "finalize"