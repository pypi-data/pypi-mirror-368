from fastsdk import FastClient, APISeex

class whisperx_video_transcribe(FastClient):
    """
    Generated client for adidoes/whisperx-video-transcribe
    """
    def __init__(self, api_key: str = None):
        super().__init__(service_name_or_id="41f4ed07-3d37-4dde-9458-09f1e308d8f1", api_key=api_key)
    
    def predictions(self, url: str, debug: bool = False, batch_size: int = 16, **kwargs) -> APISeex:
        """
        
        
        
        Args:
            url: Video URL. View supported sites https://dub.sh/supportedsites
            
            debug: Print out memory usage information. Defaults to False.
            
            batch_size: Parallelization of input audio transcription Defaults to 16.
            
        """
        return self.submit_job("/predictions", url=url, debug=debug, batch_size=batch_size, **kwargs)
    
    # Convenience aliases for the primary endpoint
    run = predictions
    __call__ = predictions