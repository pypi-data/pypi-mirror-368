from fastsdk import FastClient, APISeex

class kokoro_82m(FastClient):
    """
    Generated client for jaaari/kokoro-82m
    """
    def __init__(self, api_key: str = None):
        super().__init__(service_name_or_id="40170a05-bca7-49a3-b285-c34c28aba8ec", api_key=api_key)
    
    def predictions(self, text: str, speed: float = 1.0, voice: str = 'af_bella', **kwargs) -> APISeex:
        """
        
        
        
        Args:
            text: Text input (long text is automatically split)
            
            speed: Speech speed multiplier (0.5 = half speed, 2.0 = double speed) Defaults to 1.0.
            
            voice: Voice to use for synthesis Defaults to 'af_bella'.
            
        """
        return self.submit_job("/predictions", text=text, speed=speed, voice=voice, **kwargs)
    
    # Convenience aliases for the primary endpoint
    run = predictions
    __call__ = predictions