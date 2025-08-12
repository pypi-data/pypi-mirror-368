from fastsdk import FastClient, APISeex
from typing import Union

from media_toolkit import MediaFile


class inspyrenet(FastClient):
    """
    Generated client for swook/inspyrenet
    """
    def __init__(self, api_key: str = None):
        super().__init__(service_name_or_id="53b61825-79f2-4503-bfd0-a5538c7d3610", api_key=api_key)
    
    def predictions(self, image_path: Union[MediaFile, str, bytes], **kwargs) -> APISeex:
        """
        
        
        
        Args:
            image_path: RGB input image
            
        """
        return self.submit_job("/predictions", image_path=image_path, **kwargs)
    
    # Convenience aliases for the primary endpoint
    run = predictions
    __call__ = predictions