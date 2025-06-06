def generate_slug(text):
    return text.lower().replace(" ", "-").replace("_", "-")

def format_hashtags(hashtags):
    return [f"#{tag.strip()}" for tag in hashtags if tag.strip()]

def extract_keywords(text):
    return list(set(text.lower().split()))  # Simple keyword extraction

def validate_input(data):
    if not isinstance(data, dict):
        raise ValueError("Input must be a dictionary.")
    required_keys = ['campaign_message', 'target_audience', 'tone']
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required key: {key}")

def clean_text(text):
    return ' '.join(text.split())  # Remove extra whitespace

def generate_image_suggestions(platform):
    suggestions = {
        'instagram': ["Image of the product in use", "Behind-the-scenes shot"],
        'facebook': ["Engaging graphic", "Customer testimonial image"],
        'linkedin': ["Professional headshot", "Infographic related to the content"],
        'x': ["Trending meme", "Relevant news article screenshot"]
    }
    return suggestions.get(platform, [])