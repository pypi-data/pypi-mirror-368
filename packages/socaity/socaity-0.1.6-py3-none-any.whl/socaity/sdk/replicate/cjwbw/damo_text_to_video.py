from fastsdk import FastClient, APISeex
from typing import Optional


class damo_text_to_video(FastClient):
    """
    Generated client for cjwbw/damo-text-to-video
    """
    def __init__(self, api_key: str = None):
        super().__init__(service_name_or_id="6ab55669-b0df-4a2f-be3a-8f641973eb50", api_key=api_key)
    
    def predictions(self, fps: int = 8, prompt: str = 'An astronaut riding a horse', num_frames: int = 16, num_inference_steps: int = 50, seed: Optional[int] = None, **kwargs) -> APISeex:
        """
        
        
        
        Args:
            fps: fps for the output video Defaults to 8.
            
            prompt: Input prompt Defaults to 'An astronaut riding a horse'.
            
            num_frames: Number of frames for the output video Defaults to 16.
            
            num_inference_steps: Number of denoising steps Defaults to 50.
            
            seed: Random seed. Leave blank to randomize the seed Optional.
            
        """
        return self.submit_job("/predictions", fps=fps, prompt=prompt, num_frames=num_frames, num_inference_steps=num_inference_steps, seed=seed, **kwargs)
    
    # Convenience aliases for the primary endpoint
    run = predictions
    __call__ = predictions