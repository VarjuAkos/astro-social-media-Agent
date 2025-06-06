from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from typing import Dict, List, Optional, Any
import json
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        if settings.use_groq:
            if not settings.groq_api_key:
                raise ValueError("GROQ_API_KEY environment variable is required")
            
            self.llm = ChatGroq(
                api_key=settings.groq_api_key,
                model=settings.model_name,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens
            )
            logger.info(f"Using Groq API with model: {settings.model_name}")
        else:
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            
            self.llm = ChatOpenAI(
                api_key=settings.openai_api_key,
                model=settings.model_name,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens
            )
            logger.info(f"Using OpenAI API with model: {settings.model_name}")
    
    async def analyze_context(self, campaign_message: str, target_audience: str, tone: str) -> Dict[str, Any]:
        """First step: Analyze campaign context and generate initial ideas."""
        
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
        
        try:
            messages = [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]
            response = await self.llm.ainvoke(messages)
            
            # Try to parse JSON response
            parsed_response = json.loads(response.content)
            return parsed_response
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse context analysis response: {response.content}")
            # Return a default structure that matches expected format
            return {
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
        except Exception as e:
            logger.error(f"Context analysis failed: {e}")
            # Return a default structure instead of error dict
            return {
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
    
    async def generate_platform_posts(self, context: Dict, campaign_message: str, 
                                    target_audience: str, tone: str, use_emojis: bool) -> Dict[str, Dict]:
        """Second step: Generate platform-specific posts based on context analysis."""
        
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
        
        try:
            messages = [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]
            response = await self.llm.ainvoke(messages)
            
            # Clean the response content to extract JSON
            content = response.content.strip()
            
            # Try to find JSON in the response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_content = content[json_start:json_end]
                parsed_response = json.loads(json_content)
                logger.info("Successfully parsed posts generation response")
                return parsed_response
            else:
                raise json.JSONDecodeError("No JSON found in response", content, 0)
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse posts generation response: {content}")
            # Return fallback posts with the campaign message
            return self._generate_fallback_posts(campaign_message, target_audience, tone, use_emojis)
        except Exception as e:
            logger.error(f"Posts generation failed: {e}")
            return self._generate_fallback_posts(campaign_message, target_audience, tone, use_emojis)
    
    def _generate_fallback_posts(self, campaign_message: str, target_audience: str, 
                                tone: str, use_emojis: bool) -> Dict[str, Dict]:
        """Generate fallback posts when AI service fails."""
        emoji = "🎯" if use_emojis else ""
        
        tone_prefix = {
            "friendly": f"Szia {target_audience}! {emoji}",
            "professional": f"Tisztelt {target_audience}!",
            "humorous": f"Hahó {target_audience}! 😄" if use_emojis else f"Hahó {target_audience}!",
            "casual": f"Hey {target_audience}! {emoji}",
            "formal": f"Tisztelt {target_audience}!"
        }.get(tone, "")
        
        base_text = f"{tone_prefix} {campaign_message}"
        
        return {
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