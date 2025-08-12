from fastsdk import FastClient, APISeex
from typing import Union, Optional

from media_toolkit import MediaFile


class imagebind(FastClient):
    """
    Generated client for daanelson/imagebind
    """
    def __init__(self, api_key: str = None):
        super().__init__(service_name_or_id="9e850624-b6b5-458e-a445-56ee6b06e29b", api_key=api_key)
    
    def predictions(self, modality: str = 'vision', input: Optional[Union[MediaFile, str, bytes]] = None, text_input: Optional[str] = None, **kwargs) -> APISeex:
        """
        
        
        
        Args:
            modality: modality of the input you'd like to embed Defaults to 'vision'.
            
            input: file that you want to embed. Needs to be text, vision, or audio. Optional.
            
            text_input: text that you want to embed. Provide a string here instead of a text file to input if you'd like. Optional.
            
        """
        return self.submit_job("/predictions", modality=modality, input=input, text_input=text_input, **kwargs)
    
    # Convenience aliases for the primary endpoint
    run = predictions
    __call__ = predictions