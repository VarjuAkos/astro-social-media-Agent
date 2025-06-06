# Test Assignment – AI Social Media Agent

Regarding the test assignment below, write how you would implement it, what you would pay attention to, and what the end result would be. Send the final result in a document. If there's any part that you actually build and share, send it in the accompanying letter.

## Goal
Design and implement a mini-agent that automatically generates optimized posts for multiple platforms (Facebook, Instagram, LinkedIn, X) based on a single marketing message.

## Input
- Campaign message (1-2 sentences)
- Target audience (brief description, e.g., "25-35 year old hobby gamers")
- Tone (e.g., "friendly", "professional", "humorous")
- Optional emoji usage (yes/no)

## Output
```json
{
  "facebook": "<text + recommended hashtags>",
  "instagram": "<text + hashtags + 2 suggested image ideas>",
  "linkedin": "<text>",
  "x": "<text + hashtags>"
}
```

## Required Functionality
1. Adherence to platform-specific length and style constraints
2. Variation: at least two creative reformulations within a platform
3. Linguistic correctness in Hungarian (English words only when justified)
4. Simple API call (CLI or REST) for testing
5. Brief README: execution, parameters, extensibility

## Evaluation Criteria

| Criterion | Weight |
|-----------|--------|
| Creativity, UX-relevance | 30% |
| Code cleanliness, documentation | 25% |
| Scalability plan (e.g., prompt-pipeline, cache) | 20% |
| Error handling, test coverage | 15% |
| Runtime/installation simplicity | 10% |

## Submission Format
- Git repo or zip (code + README)
- 1 example input → JSON output
- Deadline: [date] 23:59 (CET)

## Extra Points (Optional)
- Automatic A/B labeling for generated posts for later testing
- Scheduled posting suggestion (optimal timing based on daily time slots)