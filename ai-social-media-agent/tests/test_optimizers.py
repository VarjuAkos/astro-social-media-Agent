import pytest
from src.agents.platform_optimizers.facebook_optimizer import FacebookOptimizer
from src.agents.platform_optimizers.instagram_optimizer import InstagramOptimizer
from src.agents.platform_optimizers.linkedin_optimizer import LinkedInOptimizer
from src.agents.platform_optimizers.x_optimizer import XOptimizer

def test_facebook_optimizer():
    optimizer = FacebookOptimizer()
    input_text = "Exciting news about our new product launch!"
    expected_output = {
        "text": "Exciting news about our new product launch! Check it out! #NewProduct #Launch",
        "hashtags": ["#NewProduct", "#Launch"]
    }
    assert optimizer.optimize(input_text) == expected_output

def test_instagram_optimizer():
    optimizer = InstagramOptimizer()
    input_text = "Check out our latest collection!"
    expected_output = {
        "text": "Check out our latest collection! 🌟",
        "hashtags": ["#LatestCollection", "#Fashion"],
        "image_suggestions": ["image1.jpg", "image2.jpg"]
    }
    assert optimizer.optimize(input_text) == expected_output

def test_linkedin_optimizer():
    optimizer = LinkedInOptimizer()
    input_text = "We are proud to announce our new partnership."
    expected_output = {
        "text": "We are proud to announce our new partnership. Let's connect!",
    }
    assert optimizer.optimize(input_text) == expected_output

def test_x_optimizer():
    optimizer = XOptimizer()
    input_text = "Join us for an exciting event!"
    expected_output = {
        "text": "Join us for an exciting event! Don't miss out! #Event #JoinUs",
        "hashtags": ["#Event", "#JoinUs"]
    }
    assert optimizer.optimize(input_text) == expected_output

if __name__ == "__main__":
    pytest.main()