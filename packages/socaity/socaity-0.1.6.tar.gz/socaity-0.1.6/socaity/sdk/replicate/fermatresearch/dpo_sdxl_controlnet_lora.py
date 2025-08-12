from fastsdk import FastClient, APISeex
from typing import Union, Optional

from media_toolkit import MediaFile


class dpo_sdxl_controlnet_lora(FastClient):
    """
    Generated client for fermatresearch/dpo-sdxl-controlnet-lora
    """
    def __init__(self, api_key: str = None):
        super().__init__(service_name_or_id="6a593e8f-bde8-40a4-a970-aae7d7566548", api_key=api_key)
    
    def predictions(self, prompt: str = 'An astronaut riding a rainbow unicorn', refine: str = 'base_image_refiner', scheduler: str = 'K_EULER', lora_scale: float = 0.6, num_outputs: int = 1, refine_steps: int = 10, guidance_scale: float = 7.5, apply_watermark: bool = True, condition_scale: float = 0.5, negative_prompt: str = '', num_inference_steps: int = 50, seed: Optional[int] = None, image: Optional[Union[MediaFile, str, bytes]] = None, lora_weights: Optional[str] = None, **kwargs) -> APISeex:
        """
        
        
        
        Args:
            prompt: Input prompt Defaults to 'An astronaut riding a rainbow unicorn'.
            
            refine: Whether to use refinement steps or not Defaults to 'base_image_refiner'.
            
            scheduler: scheduler Defaults to 'K_EULER'.
            
            lora_scale: LoRA additive scale. Only applicable on trained models. Defaults to 0.6.
            
            num_outputs: Number of images to output Defaults to 1.
            
            refine_steps: For base_image_refiner, the number of steps to refine Defaults to 10.
            
            guidance_scale: Scale for classifier-free guidance Defaults to 7.5.
            
            apply_watermark: Applies a watermark to enable determining if an image is generated in downstream applications. If you have other provisions for generating or deploying images safely, you can use this to disable watermarking. Defaults to True.
            
            condition_scale: The bigger this number is, the more ControlNet interferes Defaults to 0.5.
            
            negative_prompt: Input Negative Prompt Defaults to ''.
            
            num_inference_steps: Number of denoising steps Defaults to 50.
            
            seed: Random seed. Leave blank to randomize the seed Optional.
            
            image: Input image for img2img or inpaint mode Optional.
            
            lora_weights: Replicate LoRA weights to use. Leave blank to use the default weights. Optional.
            
        """
        return self.submit_job("/predictions", prompt=prompt, refine=refine, scheduler=scheduler, lora_scale=lora_scale, num_outputs=num_outputs, refine_steps=refine_steps, guidance_scale=guidance_scale, apply_watermark=apply_watermark, condition_scale=condition_scale, negative_prompt=negative_prompt, num_inference_steps=num_inference_steps, seed=seed, image=image, lora_weights=lora_weights, **kwargs)
    
    # Convenience aliases for the primary endpoint
    run = predictions
    __call__ = predictions