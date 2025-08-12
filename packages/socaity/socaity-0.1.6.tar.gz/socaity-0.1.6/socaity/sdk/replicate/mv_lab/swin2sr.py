from fastsdk import FastClient, APISeex
from typing import Union

from media_toolkit import MediaFile


class swin2sr(FastClient):
    """
    Generated client for mv-lab/swin2sr
    """
    def __init__(self, api_key: str = None):
        super().__init__(service_name_or_id="6e37ff20-c897-459b-88b3-7214da99faca", api_key=api_key)
    
    def predictions(self, image: Union[MediaFile, str, bytes], task: str = 'real_sr', **kwargs) -> APISeex:
        """
        
        
        
        Args:
            image: Input image
            
            task: Choose a task Defaults to 'real_sr'.
            
        """
        return self.submit_job("/predictions", image=image, task=task, **kwargs)
    
    # Convenience aliases for the primary endpoint
    run = predictions
    __call__ = predictions