# file: app/publishers/linkedin_publisher.py
import requests
import logging
from typing import Dict, Any, Optional
from .base import BasePublisher

logger = logging.getLogger(__name__)
API_BASE = "https://api.linkedin.com/v2"

class LinkedInPublisher(BasePublisher):
    """
    Мінімалістична реалізація публікації в LinkedIn.
    Працює з ручним access_token та URN (organization або person).
    Публікує текстовий UGC пост. Для зображень потрібні додаткові завантаження (assets).
    """

    def validate_config(self) -> None:
        """Validate LinkedIn configuration"""
        required = ["access_token", "urn"]
        for f in required:
            if not self.config.get(f):
                raise ValueError(f"Missing LinkedIn config: {f}")
        self.access_token = self.config["access_token"]
        self.urn = self.config["urn"]
        logger.info(f"LinkedIn publisher initialized for URN: {self.urn}")

    def _headers(self) -> Dict[str, str]:
        """Get headers for LinkedIn API requests"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }

    def publish_text(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Publish text-only post to LinkedIn (UGC Post).
        Документація: UGC Posts API. Для image/video потрібна реєстрація asset'ів.
        """
        payload = {
            "author": self.urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
        
        try:
            logger.info(f"Publishing to LinkedIn for URN: {self.urn}")
            r = requests.post(
                f"{API_BASE}/ugcPosts", 
                json=payload, 
                headers=self._headers(), 
                timeout=30
            )
            
            ok = r.status_code in (201, 200)
            response_data = r.json() if r.text else {}
            
            if ok:
                logger.info(f"LinkedIn post published successfully: {response_data.get('id', 'N/A')}")
            else:
                logger.error(f"LinkedIn API error: {r.status_code} - {response_data}")
            
            return {
                "success": ok, 
                "status": r.status_code, 
                "response": response_data, 
                "platform": "LinkedIn"
            }
        
        except requests.RequestException as e:
            logger.error(f"LinkedIn network error: {e}")
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "platform": "LinkedIn"
            }

    def publish_image(self, text: str, image_b64: Optional[str], **kwargs) -> Dict[str, Any]:
        """
        Publish post with image (simplified - text only for now).
        Для повноцінної публікації зображень потрібна реєстрація assets через окремий API.
        """
        # TODO: Implement image upload via LinkedIn Assets API
        logger.warning("LinkedIn image upload not fully implemented - publishing text only")
        return self.publish_text(text)

    def publish_video(self, text: str, video_path: str, **kwargs) -> Dict[str, Any]:
        """Publish video (not implemented)"""
        return {
            "success": False,
            "error": "Video publishing not implemented for LinkedIn",
            "platform": "LinkedIn"
        }

    def publish(self, content_type: str, text: str, **kwargs) -> Dict[str, Any]:
        """Main publish method"""
        image_b64 = kwargs.get("image_b64")
        video_path = kwargs.get("video_path")
        
        if video_path:
            return self.publish_video(text, video_path, **kwargs)
        elif image_b64:
            return self.publish_image(text, image_b64, **kwargs)
        else:
            return self.publish_text(text, **kwargs)
