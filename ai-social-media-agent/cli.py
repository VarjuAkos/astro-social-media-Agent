#!/usr/bin/env python3
"""
CLI interface for the AI Social Media Agent
Provides simple command-line testing capability
"""

import asyncio
import json
import argparse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.models.request_models import SocialMediaRequest, ToneType
from src.agents.social_media_agent import SocialMediaAgent

async def main():
    parser = argparse.ArgumentParser(description='AI Social Media Agent CLI')
    parser.add_argument('--message', '-m', required=True, 
                       help='Campaign message (1-2 sentences)')
    parser.add_argument('--audience', '-a', required=True,
                       help='Target audience description')
    parser.add_argument('--tone', '-t', 
                       choices=[tone.value for tone in ToneType],
                       default='friendly',
                       help='Tone of the posts')
    parser.add_argument('--no-emojis', action='store_true',
                       help='Disable emoji usage')
    parser.add_argument('--output', '-o', 
                       help='Output file for JSON result')
    
    args = parser.parse_args()
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is required")
        print("Please set it in your .env file or environment")
        return 1
    
    try:
        # Create request
        request = SocialMediaRequest(
            campaign_message=args.message,
            target_audience=args.audience,
            tone=ToneType(args.tone),
            use_emojis=not args.no_emojis
        )
        
        print(f"🤖 Generating posts for: {args.message}")
        print(f"👥 Target audience: {args.audience}")
        print(f"🎭 Tone: {args.tone}")
        print("⏳ Processing...")
        
        # Initialize agent and process
        agent = SocialMediaAgent()
        result = await agent.process_request(request)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return 1
        
        # Output results
        print("\n✅ Posts generated successfully!\n")
        
        # Pretty print JSON
        formatted_result = json.dumps(result, indent=2, ensure_ascii=False)
        print(formatted_result)
        
        # Save to file if requested
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Results saved to: {args.output}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())