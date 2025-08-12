from fastsdk import FastClient, APISeex

class snowflake_arctic_embed_l(FastClient):
    """
    Generated client for lucataco/snowflake-arctic-embed-l
    """
    def __init__(self, api_key: str = None):
        super().__init__(service_name_or_id="a206aeb5-dedd-408f-a3c3-818383d682bb", api_key=api_key)
    
    def predictions(self, prompt: str = 'Snowflake is the Data Cloud!', **kwargs) -> APISeex:
        """
        
        
        
        Args:
            prompt: Prompt to generate a vector embedding for Defaults to 'Snowflake is the Data Cloud!'.
            
        """
        return self.submit_job("/predictions", prompt=prompt, **kwargs)
    
    # Convenience aliases for the primary endpoint
    run = predictions
    __call__ = predictions