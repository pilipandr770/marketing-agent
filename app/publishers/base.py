# file: app/publishers/base.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class BasePublisher(ABC):
    """Base class for social media publishers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.validate_config()
    
    @abstractmethod
    def validate_config(self) -> None:
        """Validate publisher configuration"""
        pass
    
    @abstractmethod
    def publish_text(self, text: str, **kwargs) -> Dict[str, Any]:
        """Publish text content"""
        pass
    
    @abstractmethod
    def publish_image(self, text: str, image_b64: str, **kwargs) -> Dict[str, Any]:
        """Publish image with text"""
        pass
    
    @abstractmethod
    def publish_video(self, text: str, video_path: str, **kwargs) -> Dict[str, Any]:
        """Publish video with text"""
        pass
    
    def publish(self, content_type: str, text: str, 
                image_b64: Optional[str] = None,
                voice_bytes: Optional[bytes] = None,
                **kwargs) -> Dict[str, Any]:
        """
        Universal publish method
        
        Args:
            content_type: Type of content (post, story, reel)
            text: Text content
            image_b64: Base64 encoded image
            voice_bytes: Audio bytes
            **kwargs: Additional parameters
        
        Returns:
            Dict with publication result
        """
        try:
            if image_b64:
                # Remove image_b64 from kwargs to avoid duplicate argument error
                kwargs_copy = kwargs.copy()
                kwargs_copy.pop('image_b64', None)
                return self.publish_image(text, image_b64, **kwargs_copy)
            else:
                return self.publish_text(text, **kwargs)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "platform": self.__class__.__name__
            }