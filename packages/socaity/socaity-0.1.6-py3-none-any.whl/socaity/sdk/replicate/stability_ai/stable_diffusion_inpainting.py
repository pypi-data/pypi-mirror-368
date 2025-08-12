from fastsdk import FastClient, APISeex
from typing import Union, Optional

from media_toolkit import MediaFile


class stable_diffusion_inpainting(FastClient):
    """
    Generated client for stability-ai/stable-diffusion-inpainting
    """
    def __init__(self, api_key: str = None):
        super().__init__(service_name_or_id="d5e66f27-1249-4db2-9f73-651c156399ad", api_key=api_key)
    
    def predictions(self, mask: Union[MediaFile, str, bytes], image: Union[MediaFile, str, bytes], width: int = 512, height: int = 512, prompt: str = 'a vision of paradise. unreal engine', scheduler: str = 'DPMSolverMultistep', num_outputs: int = 1, guidance_scale: float = 7.5, num_inference_steps: int = 50, disable_safety_checker: bool = False, seed: Optional[int] = None, negative_prompt: Optional[str] = None, **kwargs) -> APISeex:
        """
        
        
        
        Args:
            mask: Black and white image to use as mask for inpainting over the image provided. White pixels are inpainted and black pixels are preserved.
            
            image: Initial image to generate variations of. Will be resized to height x width
            
            width: Width of generated image in pixels. Needs to be a multiple of 64 Defaults to 512.
            
            height: Height of generated image in pixels. Needs to be a multiple of 64 Defaults to 512.
            
            prompt: Input prompt Defaults to 'a vision of paradise. unreal engine'.
            
            scheduler: Choose a scheduler. Defaults to 'DPMSolverMultistep'.
            
            num_outputs: Number of images to generate. Defaults to 1.
            
            guidance_scale: Scale for classifier-free guidance Defaults to 7.5.
            
            num_inference_steps: Number of denoising steps Defaults to 50.
            
            disable_safety_checker: Disable safety checker for generated images. This feature is only available through the API. See [https://replicate.com/docs/how-does-replicate-work#safety](https://replicate.com/docs/how-does-replicate-work#safety) Defaults to False.
            
            seed: Random seed. Leave blank to randomize the seed Optional.
            
            negative_prompt: Specify things to not see in the output Optional.
            
        """
        return self.submit_job("/predictions", mask=mask, image=image, width=width, height=height, prompt=prompt, scheduler=scheduler, num_outputs=num_outputs, guidance_scale=guidance_scale, num_inference_steps=num_inference_steps, disable_safety_checker=disable_safety_checker, seed=seed, negative_prompt=negative_prompt, **kwargs)
    
    # Convenience aliases for the primary endpoint
    run = predictions
    __call__ = predictions