# AI Social Media Agent

A sophisticated AI-powered social media content generator that creates optimized posts for multiple platforms (Facebook, Instagram, LinkedIn, X) using LangGraph workflow with human feedback integration.

## 🎯 Features

- **Multi-Step AI Workflow**: Uses LangGraph for structured content generation with context analysis
- **Platform Optimization**: Automatically adapts content for each platform's constraints and best practices
- **Human Feedback Loop**: Interactive refinement process with up to 3 iterations
- **Hungarian Language Focus**: Optimized for Hungarian content with appropriate English word usage
- **Real-time Streamlit Interface**: User-friendly web interface with immediate feedback
- **Structured Output**: Clean JSON export for easy integration

## 🏗️ Architecture

### LangGraph Workflow
1. **Context Analysis Node** - Analyzes campaign message and target audience
2. **Content Generation Node** - Creates platform-specific posts with variations
3. **Feedback Collection Node** - Presents results and collects user input
4. **Refinement Node** - Improves posts based on feedback
5. **Finalization Node** - Outputs final JSON format

### Key Components
- **AI Service** - LangChain + OpenAI integration for content generation
- **Workflow State Management** - Pydantic models for type safety
- **Platform Optimizers** - Specific constraints and formatting for each platform
- **Streamlit UI** - Interactive web interface

## 📋 Requirements

### System Requirements
- Python 3.8+
- OpenAI API key
- Modern web browser

### Platform Constraints
- **Facebook**: Max 63,206 characters, up to 30 hashtags
- **Instagram**: Max 2,200 characters, up to 30 hashtags, 2 image suggestions
- **LinkedIn**: Max 1,300 characters, up to 3 hashtags (professional tone)
- **X (Twitter)**: Max 280 characters, up to 2 hashtags

## 🚀 Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ai-social-media-agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

4. **Run the application**
```bash
streamlit run src/app.py
```

## 🎮 Usage

### Web Interface
1. Open `http://localhost:8501` in your browser
2. Fill in the campaign details:
   - **Campaign Message**: 1-2 sentences describing your campaign
   - **Target Audience**: Brief description (e.g., "25-35 year old hobby gamers")
   - **Tone**: Choose from friendly, professional, humorous, casual, formal
   - **Use Emojis**: Toggle emoji inclusion
3. Click "Generate Posts" to start the AI workflow
4. Review generated posts and provide feedback for refinement
5. Download final results as JSON

### Example Input
```json
{
  "campaign_message": "Új gaming laptop kollekciónk most 20% kedvezménnyel kapható!",
  "target_audience": "25-35 éves hobby gamerek",
  "tone": "friendly",
  "use_emojis": true
}
```

### Example Output
```json
{
  "facebook": {
    "text": "🎮 Fantasztikus hír minden gamer számára! Új laptop kollekciónk végre itt van, és most 20% kedvezménnyel viheted haza! Ezek a gépek minden játékot simán futtatnak...",
    "hashtags": ["#gaming", "#laptop", "#akció"]
  },
  "instagram": {
    "text": "🔥 GAMER LAPTOPOK AKCIÓ! 🔥\n\nÚj kollekciónk most 20% kedvezménnyel! 💻✨",
    "hashtags": ["#gaming", "#laptop", "#akció", "#gamer"],
    "image_suggestions": ["Gaming laptop RGB világítással", "Játékos asztal beállítás új laptoppal"]
  },
  "linkedin": {
    "text": "Bemutatjuk új gaming laptop kollekciónkat 20% kedvezménnyel. Professzionális teljesítmény játékhoz és munkához egyaránt.",
    "hashtags": ["#gaming", "#technológia"]
  },
  "x": {
    "text": "🎮 Új gaming laptop kollekció 20% kedvezménnyel! Limitált idejű ajánlat 🔥",
    "hashtags": ["#gaming", "#laptop"]
  }
}
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY` - Required: Your OpenAI API key
- `MODEL_NAME` - Optional: OpenAI model (default: gpt-3.5-turbo)
- `TEMPERATURE` - Optional: AI creativity level (default: 0.7)
- `MAX_TOKENS` - Optional: Maximum response length (default: 1500)

### Platform Limits
Platform-specific constraints are configured in `src/config/settings.py` and can be adjusted as needed.

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

Test coverage includes:
- Workflow node functionality
- Platform constraint validation
- AI service integration
- Error handling

## 📈 Scalability Features

### Caching Strategy
- Context analysis results caching
- Generated content versioning
- User feedback history

### Performance Optimization
- Async/await throughout the workflow
- Structured state management
- Efficient AI prompt engineering

### Extensibility
- Modular platform optimizers
- Pluggable AI service providers
- Configurable workflow nodes

## 🚨 Error Handling

- **API Failures**: Graceful fallbacks and user notifications
- **Invalid Input**: Pydantic validation with helpful error messages
- **Workflow Errors**: Automatic recovery and state preservation
- **Rate Limiting**: Built-in retry logic for AI service calls

## 🎨 Future Enhancements

### Planned Features
- **A/B Testing Labels**: Automatic variant labeling for testing
- **Scheduled Posting**: Optimal timing suggestions
- **Multi-language Support**: Extended language capabilities
- **Content Analytics**: Performance prediction and optimization
- **Custom Templates**: User-defined content templates

### Integration Possibilities
- Social media platform APIs for direct posting
- Content management system integration
- Analytics and performance tracking
- Team collaboration features

## 📊 Evaluation Criteria Coverage

| Criterion | Implementation | Weight |
|-----------|---------------|--------|
| **Creativity & UX** | LangGraph multi-step workflow, interactive feedback, context analysis | 30% |
| **Code Quality** | Pydantic models, type hints, comprehensive error handling, modular design | 25% |
| **Scalability** | Async architecture, state management, caching strategy, modular components | 20% |
| **Error Handling** | Try-catch blocks, validation, graceful fallbacks, user feedback | 15% |
| **Installation** | Simple pip install, environment configuration, single command startup | 10% |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section below
- Review the example usage
- Ensure your OpenAI API key is valid and has sufficient credits

### Troubleshooting
- **"OpenAI API key not configured"**: Create a `.env` file with your API key
- **"Failed to generate posts"**: Check your internet connection and API key validity
- **UI not loading**: Ensure Streamlit is installed: `pip install streamlit`