# file: app/publishers/telegram_publisher.py
import base64
import requests
from typing import Dict, Any, Optional
from .base import BasePublisher
import logging

logger = logging.getLogger(__name__)

class TelegramPublisher(BasePublisher):
    """Telegram publisher using Bot API"""
    
    def validate_config(self) -> None:
        """Validate Telegram configuration"""
        required_fields = ['bot_token', 'chat_id']
        for field in required_fields:
            if not self.config.get(field):
                raise ValueError(f"Missing required Telegram config: {field}")
        
        self.bot_token = self.config['bot_token']
        self.chat_id = str(self.config['chat_id']).strip()
        
        # Normalize chat_id format
        # If it's a channel name without @, add it
        if self.chat_id and not self.chat_id.startswith('@') and not self.chat_id.startswith('-') and not self.chat_id.isdigit():
            self.chat_id = f"@{self.chat_id}"
        
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        logger.info(f"Telegram publisher initialized for chat_id: {self.chat_id}")
    
    def _make_request(self, method: str, data: Dict[str, Any], files: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make API request to Telegram"""
        url = f"{self.base_url}/{method}"
        
        try:
            logger.info(f"Sending Telegram request to {method} for chat_id: {data.get('chat_id')}")
            
            if files:
                response = requests.post(url, data=data, files=files, timeout=30)
            else:
                response = requests.post(url, json=data, timeout=30)
            
            # Check for Telegram API errors even with 200 status
            response_data = response.json()
            if not response_data.get('ok'):
                error_msg = response_data.get('description', 'Unknown Telegram API error')
                logger.error(f"Telegram API returned error: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "platform": "Telegram"
                }
            
            response.raise_for_status()
            logger.info(f"Telegram message sent successfully to {data.get('chat_id')}")
            return {
                "success": True,
                "response": response_data,
                "platform": "Telegram"
            }
        
        except requests.RequestException as e:
            logger.error(f"Telegram API network error: {e}")
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "platform": "Telegram"
            }
    
    def publish_text(self, text: str, **kwargs) -> Dict[str, Any]:
        """Publish text message to Telegram"""
        data = {
            "chat_id": self.chat_id,
            "text": text[:4096],  # Telegram limit
            "parse_mode": kwargs.get("parse_mode", "HTML"),
            "disable_web_page_preview": kwargs.get("disable_preview", False)
        }
        
        return self._make_request("sendMessage", data)
    
    def publish_image(self, text: str, image_b64: str, **kwargs) -> Dict[str, Any]:
        """Publish image with caption to Telegram"""
        try:
            image_bytes = base64.b64decode(image_b64)
            
            files = {
                "photo": ("image.jpg", image_bytes, "image/jpeg")
            }
            
            data = {
                "chat_id": self.chat_id,
                "caption": text[:1024],  # Telegram caption limit
                "parse_mode": kwargs.get("parse_mode", "HTML")
            }
            
            return self._make_request("sendPhoto", data, files)
        
        except Exception as e:
            logger.error(f"Error publishing image to Telegram: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform": "Telegram"
            }
    
    def publish_video(self, text: str, video_path: str, **kwargs) -> Dict[str, Any]:
        """Publish video with caption to Telegram"""
        try:
            with open(video_path, 'rb') as video_file:
                files = {
                    "video": (video_path, video_file, "video/mp4")
                }
                
                data = {
                    "chat_id": self.chat_id,
                    "caption": text[:1024],
                    "parse_mode": kwargs.get("parse_mode", "HTML")
                }
                
                return self._make_request("sendVideo", data, files)
        
        except Exception as e:
            logger.error(f"Error publishing video to Telegram: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform": "Telegram"
            }
    
    def publish_voice(self, voice_bytes: bytes, **kwargs) -> Dict[str, Any]:
        """Publish voice message to Telegram"""
        try:
            files = {
                "voice": ("voice.ogg", voice_bytes, "audio/ogg")
            }
            
            data = {
                "chat_id": self.chat_id,
                "duration": kwargs.get("duration"),
                "caption": kwargs.get("caption", "")[:1024]
            }
            
            return self._make_request("sendVoice", data, files)
        
        except Exception as e:
            logger.error(f"Error publishing voice to Telegram: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform": "Telegram"
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Telegram bot connection"""
        return self._make_request("getMe", {})