# file: app/openai_service.py
import os
import base64
from typing import Optional, Tuple, Dict, Any
from openai import OpenAI
import httpx
import logging

logger = logging.getLogger(__name__)

def get_openai_client(user_api_key: Optional[str] = None) -> OpenAI:
    """Get OpenAI client with user's API key or fallback to system key"""
    api_key = user_api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("No OpenAI API key available")
    
    try:
        # Create custom HTTP client without proxies parameter
        http_client = httpx.Client(
            timeout=60.0,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        return OpenAI(api_key=api_key, http_client=http_client)
    except Exception as e:
        logger.warning(f"OpenAI client initialization error: {e}")
        # Fallback: try default initialization
        try:
            return OpenAI(api_key=api_key)
        except Exception as fallback_error:
            logger.error(f"OpenAI client fallback error: {fallback_error}")
            raise

def build_system_prompt(user_system_prompt: Optional[str], channel: str) -> str:
    """Build system prompt based on channel and user preferences"""
    
    channel_prompts = {
        "telegram": (
            "Du bist ein Experte für Telegram-Marketing. Erstelle prägnante, "
            "engaging Posts für Telegram-Kanäle. Nutze Emojis sparsam aber effektiv. "
            "Schreibe auf Deutsch und halte dich an 2000 Zeichen Limit."
        ),
        "linkedin": (
            "Du bist ein LinkedIn-Content-Experte. Erstelle professionelle, "
            "business-orientierte Posts die Engagement fördern. Nutze relevante "
            "Hashtags und einen Call-to-Action. Schreibe auf Deutsch."
        ),
        "facebook": (
            "Du bist ein Facebook-Marketing-Spezialist. Erstelle engaging Posts "
            "die Interaktion fördern. Nutze einen conversational Ton und "
            "relevante Hashtags. Schreibe auf Deutsch."
        ),
        "instagram": (
            "Du bist ein Instagram-Content-Creator. Erstelle visuell ansprechende "
            "Post-Texte mit relevanten Hashtags. Nutze einen modernen, trendigen "
            "Ton. Schreibe auf Deutsch und limitiere auf 2200 Zeichen."
        )
    }
    
    base_prompt = channel_prompts.get(channel, channel_prompts["telegram"])
    
    if user_system_prompt:
        base_prompt += f"\n\nZusätzliche Anweisungen: {user_system_prompt}"
    
    return base_prompt

def generate_post_text(topic: str, channel: str, system_prompt: str, user_api_key: Optional[str] = None) -> str:
    """Generate social media post text using OpenAI"""
    try:
        client = get_openai_client(user_api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"""
Erstelle einen {channel}-Post zum folgenden Thema: {topic}

Anforderungen:
- Authentisch und engaging
- Passend für die Zielgruppe
- Inkludiere relevante Hashtags (3-5 Stück)
- Call-to-Action wenn angebracht
- Optimale Länge für die Plattform
"""}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        logger.error(f"Error generating post text: {e}")
        return f"Fehler bei der Content-Generierung: {str(e)}"

def generate_image_prompt(topic: str, channel: str) -> str:
    """Generate image prompt based on topic and channel"""
    channel_styles = {
        "instagram": "modern, aesthetic, high-quality, Instagram-style",
        "facebook": "engaging, colorful, social media friendly",
        "linkedin": "professional, business-appropriate, clean",
        "telegram": "clear, simple, informative"
    }
    
    style = channel_styles.get(channel, "modern, clean, professional")
    
    return f"""
Create a {style} image for social media about: {topic}
- High resolution (1024x1024)
- Suitable for {channel}
- Modern design
- No text overlays
- Engaging and eye-catching
"""

def generate_image_b64(topic: str, channel: str, user_api_key: Optional[str] = None) -> Optional[str]:
    """Generate image using DALL-E and return base64"""
    try:
        client = get_openai_client(user_api_key)
        prompt = generate_image_prompt(topic, channel)
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            response_format="b64_json",
            n=1
        )
        
        return response.data[0].b64_json
    
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        return None

def generate_tts_audio(text: str, user_api_key: Optional[str] = None) -> Optional[bytes]:
    """Generate TTS audio using OpenAI"""
    try:
        client = get_openai_client(user_api_key)
        
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text[:4096],  # Limit text length
            response_format="mp3"
        )
        
        return response.read()
    
    except Exception as e:
        logger.error(f"Error generating TTS: {e}")
        return None

def upload_file_to_openai(file_path: str, purpose: str = "assistants", user_api_key: Optional[str] = None) -> Optional[str]:
    """Upload file to OpenAI and return file ID"""
    try:
        client = get_openai_client(user_api_key)
        
        with open(file_path, "rb") as file:
            response = client.files.create(
                file=file,
                purpose=purpose
            )
        
        return response.id
    
    except TypeError as e:
        logger.error(f"OpenAI API compatibility error uploading file: {e}")
        return None
    except Exception as e:
        logger.error(f"Error uploading file to OpenAI: {e}")
        return None

def add_file_to_vector_store(file_id: str, vector_store_id: str, user_api_key: Optional[str] = None) -> bool:
    """Add file to vector store"""
    try:
        client = get_openai_client(user_api_key)
        
        client.beta.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file_id
        )
        
        return True
    
    except Exception as e:
        logger.error(f"Error adding file to vector store: {e}")
        return False

def create_vector_store(name: str, user_api_key: Optional[str] = None) -> Optional[str]:
    """Create a new vector store"""
    try:
        client = get_openai_client(user_api_key)
        
        response = client.beta.vector_stores.create(
            name=name
        )
        
        return response.id
    
    except Exception as e:
        logger.error(f"Error creating vector store: {e}")
        return None