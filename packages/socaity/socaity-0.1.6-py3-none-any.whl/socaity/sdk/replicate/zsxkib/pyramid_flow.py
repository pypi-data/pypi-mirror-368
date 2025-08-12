from fastsdk import FastClient, APISeex
from typing import Union, Optional

from media_toolkit import MediaFile


class pyramid_flow(FastClient):
    """
    Generated client for zsxkib/pyramid-flow
    """
    def __init__(self, api_key: str = None):
        super().__init__(service_name_or_id="0ad6dc5a-4aeb-41e0-ad3b-083361dfe04b", api_key=api_key)
    
    def predictions(self, prompt: str, duration: int = 3, guidance_scale: float = 9.0, frames_per_second: int = 8, video_guidance_scale: float = 5.0, image: Optional[Union[MediaFile, str, bytes]] = None, **kwargs) -> APISeex:
        """
        
        
        
        Args:
            prompt: Text prompt for video generation
            
            duration: Duration of the video in seconds (1-3 for canonical mode, 1-10 for non-canonical mode) Defaults to 3.
            
            guidance_scale: Guidance Scale for text-to-video generation Defaults to 9.0.
            
            frames_per_second: Frames per second (8 or 24, only applicable in canonical mode) Defaults to 8.
            
            video_guidance_scale: Video Guidance Scale Defaults to 5.0.
            
            image: Optional input image for image-to-video generation Optional.
            
        """
        return self.submit_job("/predictions", prompt=prompt, duration=duration, guidance_scale=guidance_scale, frames_per_second=frames_per_second, video_guidance_scale=video_guidance_scale, image=image, **kwargs)
    
    # Convenience aliases for the primary endpoint
    run = predictions
    __call__ = predictions