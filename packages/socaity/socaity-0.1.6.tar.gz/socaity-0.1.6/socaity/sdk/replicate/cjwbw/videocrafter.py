from fastsdk import FastClient, APISeex
from typing import Optional


class videocrafter(FastClient):
    """
    Generated client for cjwbw/videocrafter
    """
    def __init__(self, api_key: str = None):
        super().__init__(service_name_or_id="08be5d85-7e6f-418c-a99f-e46d51f39428", api_key=api_key)
    
    def predictions(self, prompt: str = 'With the style of van gogh, A young couple dances under the moonlight by the lake.', save_fps: int = 10, ddim_steps: int = 50, unconditional_guidance_scale: float = 12.0, seed: Optional[int] = None, **kwargs) -> APISeex:
        """
        
        
        
        Args:
            prompt: Prompt for video generation. Defaults to 'With the style of van gogh, A young couple dances under the moonlight by the lake.'.
            
            save_fps: Frame per second for the generated video. Defaults to 10.
            
            ddim_steps: Number of denoising steps. Defaults to 50.
            
            unconditional_guidance_scale: Classifier-free guidance scale. Defaults to 12.0.
            
            seed: Random seed. Leave blank to randomize the seed Optional.
            
        """
        return self.submit_job("/predictions", prompt=prompt, save_fps=save_fps, ddim_steps=ddim_steps, unconditional_guidance_scale=unconditional_guidance_scale, seed=seed, **kwargs)
    
    # Convenience aliases for the primary endpoint
    run = predictions
    __call__ = predictions