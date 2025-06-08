from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage
from config.settings import settings
import logging
import json
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        self.llm = ChatGroq(
            api_key=settings.groq_api_key,
            model=settings.model_name,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens
        )
        logger.info(f"Using Groq API with model: {settings.model_name}")
        print(f"🤖 AI Service initialized with Groq model: {settings.model_name}")
    
    async def analyze_context(self, campaign_message: str, target_audience: str, tone: str) -> Dict[str, Any]:
        """First step: Analyze campaign context and generate initial ideas."""
        
        print("\n🔍 AI SERVICE: CONTEXT ANALYSIS")
        print("-" * 50)
        
        system_prompt = """
        Te egy kreatív magyar marketing szakértő vagy. A feladatod hogy elemezd a kampányüzenetet és célközönséget, 
        majd ötleteket generálj a különböző közösségi média platformokra.
        
        Fontossági sorrend:
        1. Magyar nyelv használata (angol szavak csak indokolt esetben)
        2. Platform-specifikus stílus és korlátok figyelembevétele
        3. Célközönség sajátosságainak megértése
        4. Kreatív és engaging tartalom létrehozása
        """
        
        human_prompt = f"""
        Kampányüzenet: {campaign_message}
        Célközönség: {target_audience}
        Hangnem: {tone}
        
        Elemezd a kampány kontextusát és adj vissza:
        1. Kulcsüzenetek azonosítása
        2. Célközönség motivációi és érdeklődési területei
        3. Platform-specifikus megközelítési stratégiák
        4. Kreatív irányok és ötletek
        
        Válaszold JSON formátumban:
        {{
            "key_messages": ["üzenet1", "üzenet2"],
            "audience_insights": "célközönség elemzése",
            "platform_strategies": {{
                "facebook": "stratégia",
                "instagram": "stratégia", 
                "linkedin": "stratégia",
                "x": "stratégia"
            }},
            "creative_directions": ["irány1", "irány2", "irány3"]
        }}
        """
        
        print("📤 SENDING TO AI:")
        print(f"   System Prompt: {system_prompt[:100]}...")
        print(f"   Human Prompt: {human_prompt[:200]}...")
        print("   Full prompts logged below:")
        print("\n🔧 FULL SYSTEM PROMPT:")
        print(system_prompt)
        print("\n📝 FULL HUMAN PROMPT:")
        print(human_prompt)
        
        try:
            messages = [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]
            print("\n⏳ Sending request to Groq API...")
            response = await self.llm.ainvoke(messages)
            
            print(f"\n📥 RAW AI RESPONSE:")
            print(f"   Length: {len(response.content)} characters")
            print(f"   Content: {response.content}")
            
            # Try to parse JSON response
            parsed_response = json.loads(response.content)
            print(f"\n✅ PARSED JSON RESPONSE:")
            print(json.dumps(parsed_response, indent=2, ensure_ascii=False))
            return parsed_response
            
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON PARSE ERROR: {e}")
            print(f"   Raw content: {response.content}")
            logger.error(f"Failed to parse context analysis response: {response.content}")
            # Return a default structure that matches expected format
            fallback = {
                "key_messages": ["Kampány üzenet elemzése"],
                "audience_insights": f"Célközönség: {target_audience}",
                "platform_strategies": {
                    "facebook": "Részletes tartalom megosztása",
                    "instagram": "Vizuális tartalom hangsúlyozása", 
                    "linkedin": "Professzionális megközelítés",
                    "x": "Rövid, tömör üzenetek"
                },
                "creative_directions": ["Engaging tartalom", "Platform-specifikus optimalizáció", "Célközönség-fókusz"]
            }
            print(f"🔄 Using fallback response: {json.dumps(fallback, indent=2, ensure_ascii=False)}")
            return fallback
        except Exception as e:
            print(f"\n❌ AI SERVICE ERROR: {e}")
            logger.error(f"Context analysis failed: {e}")
            # Return a default structure instead of error dict
            fallback = {
                "key_messages": ["Kampány üzenet"],
                "audience_insights": f"Célközönség: {target_audience}",
                "platform_strategies": {
                    "facebook": "Általános stratégia",
                    "instagram": "Vizuális tartalom", 
                    "linkedin": "Professzionális tartalom",
                    "x": "Rövid tartalom"
                },
                "creative_directions": ["Kreatív megközelítés"]
            }
            print(f"🔄 Using fallback response due to error: {json.dumps(fallback, indent=2, ensure_ascii=False)}")
            return fallback
    
    async def generate_platform_posts(self, context: Dict, campaign_message: str, 
                                    target_audience: str, tone: str, use_emojis: bool) -> Dict[str, Dict]:
        """Second step: Generate platform-specific posts based on context analysis."""
        
        print("\n📝 AI SERVICE: PLATFORM POSTS GENERATION")
        print("-" * 50)
        
        emoji_instruction = "Használj releváns emojikat" if use_emojis else "Ne használj emojikat"
        
        system_prompt = f"""
        Te egy szakértő közösségi média tartalomkészítő vagy. A feladatod hogy platform-specifikus posztokat generálj.
        
        Platform korlátok:
        - Facebook: max 63206 karakter, max 30 hashtag
        - Instagram: max 2200 karakter, max 30 hashtag, 2 kép ötlet kell
        - LinkedIn: max 1300 karakter, max 3 hashtag, professzionális hangnem
        - X (Twitter): max 280 karakter, max 2 hashtag
        
        Általános szabályok:
        - Magyar nyelv használata (angol szavak csak indokolt esetben)
        - {emoji_instruction}
        - Hashtag-ek relevancia alapján legyenek rangsorolva
        
        FONTOS: Válaszolj CSAK valid JSON formátumban, semmi mással! Ne írj semmilyen szöveget a JSON elé vagy mögé!
        """
        
        human_prompt = f"""
        Kontextus elemzés: {json.dumps(context, ensure_ascii=False)}
        Kampányüzenet: {campaign_message}
        Célközönség: {target_audience}
        Hangnem: {tone}
        
        Készíts egy optimalizált posztot minden platformra. Válaszold CSAK JSON formátumban:
        {{
            "facebook": {{
                "text": "...",
                "hashtags": ["tag1", "tag2"]
            }},
            "instagram": {{
                "text": "...",
                "hashtags": ["tag1", "tag2"],
                "image_suggestions": ["kép1", "kép2"]
            }},
            "linkedin": {{
                "text": "...",
                "hashtags": ["tag1"]
            }},
            "x": {{
                "text": "...",
                "hashtags": ["tag1"]
            }}
        }}
        """
        
        print("📤 SENDING TO AI:")
        print(f"   Context: {json.dumps(context, ensure_ascii=False)}")
        print(f"   Campaign: {campaign_message}")
        print(f"   Audience: {target_audience}")
        print(f"   Tone: {tone}")
        print(f"   Emojis: {use_emojis}")
        
        print("\n🔧 FULL SYSTEM PROMPT:")
        print(system_prompt)
        print("\n📝 FULL HUMAN PROMPT:")
        print(human_prompt)
        
        try:
            messages = [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]
            print("\n⏳ Sending request to Groq API...")
            response = await self.llm.ainvoke(messages)
            
            # Clean the response content to extract JSON
            content = response.content.strip()
            
            print(f"\n📥 RAW AI RESPONSE:")
            print(f"   Length: {len(content)} characters")
            print(f"   Content: {content}")
            
            # Try to find JSON in the response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_content = content[json_start:json_end]
                print(f"\n🔍 EXTRACTED JSON:")
                print(json_content)
                
                parsed_response = json.loads(json_content)
                print(f"\n✅ PARSED JSON RESPONSE:")
                print(json.dumps(parsed_response, indent=2, ensure_ascii=False))
                logger.info("Successfully parsed posts generation response")
                return parsed_response
            else:
                raise json.JSONDecodeError("No JSON found in response", content, 0)
                
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON PARSE ERROR: {e}")
            print(f"   Trying to extract from: {content}")
            logger.error(f"Failed to parse posts generation response: {content}")
            # Return fallback posts with the campaign message
            fallback = self._generate_fallback_posts(campaign_message, target_audience, tone, use_emojis)
            print(f"🔄 Using fallback posts: {json.dumps(fallback, indent=2, ensure_ascii=False)}")
            return fallback
        except Exception as e:
            print(f"\n❌ AI SERVICE ERROR: {e}")
            logger.error(f"Posts generation failed: {e}")
            fallback = self._generate_fallback_posts(campaign_message, target_audience, tone, use_emojis)
            print(f"🔄 Using fallback posts due to error: {json.dumps(fallback, indent=2, ensure_ascii=False)}")
            return fallback
    
    async def refine_posts(self, current_posts: Dict, feedback: str) -> Dict[str, Dict]:
        """Third step: Refine posts based on user feedback."""
        
        print("\n🔧 AI SERVICE: POST REFINEMENT")
        print("-" * 50)
        
        system_prompt = """
        Te egy szakértő közösségi média tartalomkészítő vagy. A felhasználó visszajelzést adott a meglévő posztokra, 
        és a feladatod hogy javítsd őket a visszajelzés alapján.
        
        Platform korlátok:
        - Facebook: max 63206 karakter, max 30 hashtag
        - Instagram: max 2200 karakter, max 30 hashtag, 2 kép ötlet kell
        - LinkedIn: max 1300 karakter, max 3 hashtag, professzionális hangnem
        - X (Twitter): max 280 karakter, max 2 hashtag
        
        FONTOS: Válaszolj CSAK valid JSON formátumban, semmi mással!
        """
        
        human_prompt = f"""
        Jelenlegi posztok: {json.dumps(current_posts, ensure_ascii=False)}
        
        Felhasználói visszajelzés: {feedback}
        
        Javítsd a posztokat a visszajelzés alapján. Válaszold CSAK JSON formátumban:
        {{
            "facebook": {{
                "text": "...",
                "hashtags": ["tag1", "tag2"]
            }},
            "instagram": {{
                "text": "...",
                "hashtags": ["tag1", "tag2"],
                "image_suggestions": ["kép1", "kép2"]
            }},
            "linkedin": {{
                "text": "...",
                "hashtags": ["tag1"]
            }},
            "x": {{
                "text": "...",
                "hashtags": ["tag1"]
            }}
        }}
        """
        
        print("📤 SENDING TO AI:")
        print(f"   Current posts: {json.dumps(current_posts, ensure_ascii=False)}")
        print(f"   Feedback: {feedback}")
        
        print("\n🔧 FULL SYSTEM PROMPT:")
        print(system_prompt)
        print("\n📝 FULL HUMAN PROMPT:")
        print(human_prompt)
        
        try:
            messages = [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]
            print("\n⏳ Sending refinement request to Groq API...")
            response = await self.llm.ainvoke(messages)
            
            content = response.content.strip()
            
            print(f"\n📥 RAW AI RESPONSE:")
            print(f"   Length: {len(content)} characters")
            print(f"   Content: {content}")
            
            # Try to find JSON in the response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_content = content[json_start:json_end]
                print(f"\n🔍 EXTRACTED JSON:")
                print(json_content)
                
                parsed_response = json.loads(json_content)
                print(f"\n✅ PARSED REFINEMENT RESPONSE:")
                print(json.dumps(parsed_response, indent=2, ensure_ascii=False))
                logger.info("Successfully parsed refinement response")
                return parsed_response
            else:
                raise json.JSONDecodeError("No JSON found in refinement response", content, 0)
                
        except json.JSONDecodeError as e:
            print(f"\n❌ REFINEMENT JSON PARSE ERROR: {e}")
            print(f"   Trying to extract from: {content}")
            logger.error(f"Failed to parse refinement response: {content}")
            print("🔄 Returning original posts due to parse error")
            return current_posts
        except Exception as e:
            print(f"\n❌ REFINEMENT AI SERVICE ERROR: {e}")
            logger.error(f"Posts refinement failed: {e}")
            print("🔄 Returning original posts due to error")
            return current_posts
    
    def _generate_fallback_posts(self, campaign_message: str, target_audience: str, 
                                tone: str, use_emojis: bool) -> Dict[str, Dict]:
        """Generate fallback posts when AI service fails."""
        print("\n🔄 GENERATING FALLBACK POSTS")
        print("-" * 30)
        
        emoji = "🎯" if use_emojis else ""
        
        tone_prefix = {
            "friendly": f"Szia {target_audience}! {emoji}",
            "professional": f"Tisztelt {target_audience}!",
            "humorous": f"Hahó {target_audience}! 😄" if use_emojis else f"Hahó {target_audience}!",
            "casual": f"Hey {target_audience}! {emoji}",
            "formal": f"Tisztelt {target_audience}!"
        }.get(tone, "")
        
        base_text = f"{tone_prefix} {campaign_message}"
        
        fallback = {
            "facebook": {
                "text": f"{base_text}\n\nKövess minket további frissítésekért!",
                "hashtags": ["#szakmai", "#fejlődés", "#tréning"]
            },
            "instagram": {
                "text": base_text,
                "hashtags": ["#szakmai", "#fejlődés", "#tréning", "#workshop"],
                "image_suggestions": ["Tréning fotó", "Résztvevők képe"]
            },
            "linkedin": {
                "text": f"{base_text}\n\nCsatlakozz szakmai közösségünkhöz!",
                "hashtags": ["#szakmai", "#fejlődés"]
            },
            "x": {
                "text": base_text[:250],  # Truncate for Twitter limit
                "hashtags": ["#szakmai", "#tréning"]
            }
        }
        
        print(f"📋 Generated fallback:")
        print(json.dumps(fallback, indent=2, ensure_ascii=False))
        return fallback