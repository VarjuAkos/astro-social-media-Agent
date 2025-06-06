class InstagramOptimizer:
    def __init__(self, campaign_message, target_audience, tone, use_emoji):
        self.campaign_message = campaign_message
        self.target_audience = target_audience
        self.tone = tone
        self.use_emoji = use_emoji

    def generate_post(self):
        # Generate the main post text based on the input parameters
        post_text = self._create_post_text()
        hashtags = self._generate_hashtags()
        image_suggestions = self._suggest_images()
        
        return {
            "text": post_text,
            "hashtags": hashtags,
            "image_suggestions": image_suggestions
        }

    def _create_post_text(self):
        # Logic to create post text based on tone and campaign message
        if self.tone == "friendly":
            return f"Hey there, {self.target_audience}! {self.campaign_message}"
        elif self.tone == "professional":
            return f"Attention {self.target_audience}, {self.campaign_message}"
        elif self.tone == "humorous":
            return f"LOL, {self.target_audience}! {self.campaign_message} 😂" if self.use_emoji else f"LOL, {self.target_audience}! {self.campaign_message}"
        return self.campaign_message

    def _generate_hashtags(self):
        # Generate relevant hashtags based on the campaign message
        return ["#example", "#hashtag"]

    def _suggest_images(self):
        # Suggest image ideas based on the campaign message
        return ["Image idea 1", "Image idea 2"]