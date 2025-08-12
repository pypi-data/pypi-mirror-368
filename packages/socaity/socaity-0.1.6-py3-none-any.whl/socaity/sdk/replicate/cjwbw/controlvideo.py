from fastsdk import FastClient, APISeex
from typing import Union, Optional

from media_toolkit import MediaFile


class controlvideo(FastClient):
    """
    Generated client for cjwbw/controlvideo
    """
    def __init__(self, api_key: str = None):
        super().__init__(service_name_or_id="f9e98013-d3c4-40d5-b37f-09d47e02127e", api_key=api_key)
    
    def predictions(self, video_path: Union[MediaFile, str, bytes], prompt: str = 'A striking mallard floats effortlessly on the sparkling pond.', condition: str = 'depth', video_length: int = 15, is_long_video: bool = False, guidance_scale: float = 12.5, smoother_steps: str = '19, 20', num_inference_steps: int = 50, seed: Optional[str] = None, **kwargs) -> APISeex:
        """
        
        
        
        Args:
            video_path: source video
            
            prompt: Text description of target video Defaults to 'A striking mallard floats effortlessly on the sparkling pond.'.
            
            condition: Condition of structure sequence Defaults to 'depth'.
            
            video_length: Length of synthesized video Defaults to 15.
            
            is_long_video: Whether to use hierarchical sampler to produce long video Defaults to False.
            
            guidance_scale: Scale for classifier-free guidance Defaults to 12.5.
            
            smoother_steps: Timesteps at which using interleaved-frame smoother, separate with comma Defaults to '19, 20'.
            
            num_inference_steps: Number of denoising steps Defaults to 50.
            
            seed: Random seed. Leave blank to randomize the seed Optional.
            
        """
        return self.submit_job("/predictions", video_path=video_path, prompt=prompt, condition=condition, video_length=video_length, is_long_video=is_long_video, guidance_scale=guidance_scale, smoother_steps=smoother_steps, num_inference_steps=num_inference_steps, seed=seed, **kwargs)
    
    # Convenience aliases for the primary endpoint
    run = predictions
    __call__ = predictions