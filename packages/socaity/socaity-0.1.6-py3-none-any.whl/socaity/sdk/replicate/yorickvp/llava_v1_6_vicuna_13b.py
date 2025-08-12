from fastsdk import FastClient, APISeex
from typing import List, Union, Any, Optional

from media_toolkit import MediaFile


class llava_v1_6_vicuna_13b(FastClient):
    """
    Generated client for yorickvp/llava-v1-6-vicuna-13b
    """
    def __init__(self, api_key: str = None):
        super().__init__(service_name_or_id="9c69a246-a055-453f-b326-23c2d41ac378", api_key=api_key)
    
    def predictions(self, prompt: str, top_p: float = 1.0, max_tokens: int = 1024, temperature: float = 0.2, image: Optional[Union[MediaFile, str, bytes]] = None, history: Optional[Union[List[Any], str]] = None, **kwargs) -> APISeex:
        """
        
        
        
        Args:
            prompt: Prompt to use for text generation
            
            top_p: When decoding text, samples from the top p percentage of most likely tokens; lower to ignore less likely tokens Defaults to 1.0.
            
            max_tokens: Maximum number of tokens to generate. A word is generally 2-3 tokens Defaults to 1024.
            
            temperature: Adjusts randomness of outputs, greater than 1 is random and 0 is deterministic Defaults to 0.2.
            
            image: Input image Optional.
            
            history: List of earlier chat messages, alternating roles, starting with user input. Include <image> to specify which message to attach the image to. Optional.
            
        """
        return self.submit_job("/predictions", prompt=prompt, top_p=top_p, max_tokens=max_tokens, temperature=temperature, image=image, history=history, **kwargs)
    
    # Convenience aliases for the primary endpoint
    run = predictions
    __call__ = predictions