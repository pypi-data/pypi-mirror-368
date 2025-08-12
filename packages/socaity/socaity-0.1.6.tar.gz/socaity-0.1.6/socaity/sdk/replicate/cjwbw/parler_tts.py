from fastsdk import FastClient, APISeex

class parler_tts(FastClient):
    """
    Generated client for cjwbw/parler-tts
    """
    def __init__(self, api_key: str = None):
        super().__init__(service_name_or_id="8d81994c-94a8-40bc-81a7-2c94a85f1f24", api_key=api_key)
    
    def predictions(self, prompt: str = 'Hey, how are you doing today?', description: str = 'A female speaker with a slightly low-pitched voice delivers her words quite expressively, in a very confined sounding environment with clear audio quality. She speaks very fast.', **kwargs) -> APISeex:
        """
        
        
        
        Args:
            prompt: Text for audio generation Defaults to 'Hey, how are you doing today?'.
            
            description: Provide description of the output audio Defaults to 'A female speaker with a slightly low-pitched voice delivers her words quite expressively, in a very confined sounding environment with clear audio quality. She speaks very fast.'.
            
        """
        return self.submit_job("/predictions", prompt=prompt, description=description, **kwargs)
    
    # Convenience aliases for the primary endpoint
    run = predictions
    __call__ = predictions