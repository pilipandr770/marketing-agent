# file: app/publishers/meta_publisher.py
import base64
import requests
import logging
from typing import Dict, Any, Optional
from .base import BasePublisher

logger = logging.getLogger(__name__)
GRAPH = "https://graph.facebook.com/v20.0"

class FacebookPublisher(BasePublisher):
    """
    Публікація на Facebook Page.
    Потрібні: access_token (long-lived) з pages_manage_posts, facebook_page_id.
    """

    def validate_config(self) -> None:
        """Validate Facebook configuration"""
        logger.info("Validating Facebook config...")
        logger.info(f"Config keys: {list(self.config.keys())}")
        
        for f in ["access_token", "page_id"]:
            if not self.config.get(f):
                logger.error(f"Missing Facebook config: {f}")
                raise ValueError(f"Missing Facebook config: {f}")
        
        self.access_token = self.config["access_token"]
        self.page_id = self.config["page_id"]
        
        logger.info(f"Facebook publisher initialized for page: {self.page_id}")
        logger.info(f"Access token length: {len(self.access_token) if self.access_token else 0}")

    def publish_text(self, text: str, **kwargs) -> Dict[str, Any]:
        """Publish text-only post to Facebook Page"""
        logger.info(f"FacebookPublisher.publish_text called with text length: {len(text)}")
        logger.info(f"Access token present: {bool(self.access_token)}")
        logger.info(f"Page ID: {self.page_id}")
        
        url = f"{GRAPH}/{self.page_id}/feed"
        
        try:
            logger.info(f"Publishing text to Facebook page: {self.page_id}")
            r = requests.post(
                url, 
                data={"message": text, "access_token": self.access_token}, 
                timeout=30
            )
            
            ok = r.status_code in (200, 201)
            response_data = r.json() if r.text else {}
            
            if ok:
                logger.info(f"Facebook post published successfully: {response_data.get('id', 'N/A')}")
            else:
                logger.error(f"Facebook API error: {r.status_code} - {response_data}")
                logger.error(f"Response text: {r.text}")
            
            return {
                "success": ok, 
                "status": r.status_code, 
                "response": response_data, 
                "platform": "Facebook"
            }
        
        except requests.RequestException as e:
            logger.error(f"Facebook network error: {e}")
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "platform": "Facebook"
            }

    def publish_image(self, text: str, image_b64: str, **kwargs) -> Dict[str, Any]:
        """Publish post with image to Facebook Page"""
        if not image_b64:
            return self.publish_text(text)
        
        url = f"{GRAPH}/{self.page_id}/photos"
        
        try:
            logger.info(f"Publishing image to Facebook page: {self.page_id}")
            img_bytes = base64.b64decode(image_b64)
            files = {"source": ("image.png", img_bytes)}
            data = {"caption": text, "access_token": self.access_token}
            
            r = requests.post(url, data=data, files=files, timeout=60)
            
            ok = r.status_code in (200, 201)
            response_data = r.json() if r.text else {}
            
            if ok:
                logger.info(f"Facebook image published successfully: {response_data.get('id', 'N/A')}")
            else:
                logger.error(f"Facebook API error: {r.status_code} - {response_data}")
            
            return {
                "success": ok, 
                "status": r.status_code, 
                "response": response_data, 
                "platform": "Facebook"
            }
        
        except requests.RequestException as e:
            logger.error(f"Facebook network error: {e}")
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "platform": "Facebook"
            }

    def publish_video(self, text: str, video_path: str, **kwargs) -> Dict[str, Any]:
        """Publish video (not implemented)"""
        return {
            "success": False,
            "error": "Video publishing not implemented for Facebook",
            "platform": "Facebook"
        }

    def publish(self, content_type: str, text: str, **kwargs) -> Dict[str, Any]:
        """Main publish method"""
        image_b64 = kwargs.get("image_b64")
        video_path = kwargs.get("video_path")
        
        if video_path:
            return self.publish_video(text, video_path, **kwargs)
        elif image_b64:
            # Remove image_b64 from kwargs to avoid duplicate argument error
            kwargs_copy = kwargs.copy()
            kwargs_copy.pop('image_b64', None)
            return self.publish_image(text, image_b64, **kwargs_copy)
        else:
            return self.publish_text(text, **kwargs)


class InstagramPublisher(BasePublisher):
    """
    Публікація в Instagram Business через Graph API.
    Потрібні: access_token (long-lived), instagram_business_id.
    Обмеження: для публікації фото треба завантажити в паблік URL або спершу в S3/CDN.
    """

    def validate_config(self) -> None:
        """Validate Instagram configuration"""
        for f in ["access_token", "ig_business_id"]:
            if not self.config.get(f):
                raise ValueError(f"Missing Instagram config: {f}")
        self.access_token = self.config["access_token"]
        self.ig_id = self.config["ig_business_id"]
        logger.info(f"Instagram publisher initialized for account: {self.ig_id}")

    def publish_text(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Instagram не підтримує текст-only пости.
        Потрібно завжди мати медіа (фото або відео).
        """
        logger.warning("Instagram requires media (image/video) - text-only posts not supported")
        return {
            "success": False,
            "error": "Instagram Graph вимагає image/video через ПУБЛІЧНИЙ URL (remote_url). Додай CDN/S3.",
            "platform": "Instagram"
        }

    def publish_image(self, text: str, image_b64: str, **kwargs) -> Dict[str, Any]:
        """
        Publish image to Instagram Business account.
        Потрібен remote_url (public) -> створити media container -> publish.
        """
        remote_url = kwargs.get("remote_url")
        
        if not remote_url:
            logger.error("Instagram publishing requires remote_url (public image URL)")
            return {
                "success": False,
                "error": "Потрібен remote_url (публічне посилання на зображення) для Instagram.",
                "platform": "Instagram"
            }
        
        try:
            # 1) Створити контейнер медіа
            logger.info(f"Creating Instagram media container for account: {self.ig_id}")
            create_url = f"{GRAPH}/{self.ig_id}/media"
            r1 = requests.post(create_url, data={
                "image_url": remote_url,
                "caption": text,
                "access_token": self.access_token
            }, timeout=60)
            
            if r1.status_code not in (200, 201):
                response_data = r1.json() if r1.text else {}
                logger.error(f"Instagram container creation failed: {r1.status_code} - {response_data}")
                return {
                    "success": False, 
                    "status": r1.status_code, 
                    "response": response_data, 
                    "platform": "Instagram"
                }

            container_id = r1.json().get("id")
            if not container_id:
                logger.error("Instagram API did not return container_id")
                return {
                    "success": False, 
                    "error": "Не отримано container_id від Instagram.", 
                    "platform": "Instagram"
                }

            # 2) Публікувати контейнер
            logger.info(f"Publishing Instagram media container: {container_id}")
            publish_url = f"{GRAPH}/{self.ig_id}/media_publish"
            r2 = requests.post(publish_url, data={
                "creation_id": container_id,
                "access_token": self.access_token
            }, timeout=60)
            
            ok = r2.status_code in (200, 201)
            response_data = r2.json() if r2.text else {}
            
            if ok:
                logger.info(f"Instagram post published successfully: {response_data.get('id', 'N/A')}")
            else:
                logger.error(f"Instagram publish failed: {r2.status_code} - {response_data}")
            
            return {
                "success": ok, 
                "status": r2.status_code, 
                "response": response_data, 
                "platform": "Instagram"
            }
        
        except requests.RequestException as e:
            logger.error(f"Instagram network error: {e}")
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "platform": "Instagram"
            }

    def publish_video(self, text: str, video_path: str, **kwargs) -> Dict[str, Any]:
        """Publish video (not implemented)"""
        return {
            "success": False,
            "error": "Video publishing not implemented for Instagram",
            "platform": "Instagram"
        }

    def publish(self, content_type: str, text: str, **kwargs) -> Dict[str, Any]:
        """Main publish method"""
        image_b64 = kwargs.get("image_b64")
        video_path = kwargs.get("video_path")
        remote_url = kwargs.get("remote_url")
        
        if video_path:
            return self.publish_video(text, video_path, **kwargs)
        elif image_b64 or remote_url:
            # Remove image_b64 from kwargs to avoid duplicate argument error
            kwargs_copy = kwargs.copy()
            kwargs_copy.pop('image_b64', None)
            return self.publish_image(text, image_b64, **kwargs_copy)
        else:
            return self.publish_text(text, **kwargs)
