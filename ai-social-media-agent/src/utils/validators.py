def validate_campaign_message(message):
    if not isinstance(message, str) or len(message) < 1 or len(message) > 200:
        raise ValueError("Campaign message must be a string between 1 and 200 characters.")

def validate_target_audience(audience):
    if not isinstance(audience, str) or len(audience) < 1:
        raise ValueError("Target audience must be a non-empty string.")

def validate_tone(tone):
    valid_tones = ["friendly", "professional", "humorous"]
    if tone not in valid_tones:
        raise ValueError(f"Tone must be one of the following: {', '.join(valid_tones)}.")

def validate_emoji_usage(emoji_usage):
    if not isinstance(emoji_usage, bool):
        raise ValueError("Emoji usage must be a boolean value.")