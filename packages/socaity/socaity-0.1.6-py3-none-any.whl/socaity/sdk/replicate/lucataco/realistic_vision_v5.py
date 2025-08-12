from fastsdk import FastClient, APISeex

class realistic_vision_v5(FastClient):
    """
    Generated client for lucataco/realistic-vision-v5
    """
    def __init__(self, api_key: str = None):
        super().__init__(service_name_or_id="6de057a2-3399-4e37-b37a-1829000efe17", api_key=api_key)
    
    def predictions(self, seed: int = 0, steps: int = 20, width: int = 512, height: int = 728, prompt: str = 'RAW photo, a portrait photo of a latina woman in casual clothes, natural skin, 8k uhd, high quality, film grain, Fujifilm XT3', guidance: float = 5.0, scheduler: str = 'EulerA', negative_prompt: str = '(deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime:1.4), text, close up, cropped, out of frame, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck', **kwargs) -> APISeex:
        """
        Run a single prediction on the model
        
        
        Args:
            seed: Seed (0 = random, maximum: 2147483647) Defaults to 0.
            
            steps:  num_inference_steps Defaults to 20.
            
            width: Width Defaults to 512.
            
            height: Height Defaults to 728.
            
            prompt: prompt Defaults to 'RAW photo, a portrait photo of a latina woman in casual clothes, natural skin, 8k uhd, high quality, film grain, Fujifilm XT3'.
            
            guidance: Guidance scale (3.5 - 7) Defaults to 5.0.
            
            scheduler: Choose a scheduler Defaults to 'EulerA'.
            
            negative_prompt: negative_prompt Defaults to '(deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime:1.4), text, close up, cropped, out of frame, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck'.
            
        """
        return self.submit_job("/predictions", seed=seed, steps=steps, width=width, height=height, prompt=prompt, guidance=guidance, scheduler=scheduler, negative_prompt=negative_prompt, **kwargs)
    
    # Convenience aliases for the primary endpoint
    run = predictions
    __call__ = predictions