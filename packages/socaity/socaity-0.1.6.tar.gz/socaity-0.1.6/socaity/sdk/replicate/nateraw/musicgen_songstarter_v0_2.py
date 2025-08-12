from fastsdk import FastClient, APISeex
from typing import Union, Optional

from media_toolkit import MediaFile


class musicgen_songstarter_v0_2(FastClient):
    """
    Generated client for nateraw/musicgen-songstarter-v0-2
    """
    def __init__(self, api_key: str = None):
        super().__init__(service_name_or_id="80ce2df6-ac1d-48a3-a3f2-b164022a211f", api_key=api_key)
    
    def predictions(self, top_k: int = 250, top_p: float = 0.0, duration: int = 8, temperature: float = 1.0, continuation: bool = False, output_format: str = 'wav', continuation_start: int = 0, normalization_strategy: str = 'loudness', classifier_free_guidance: int = 3, seed: Optional[int] = None, prompt: Optional[str] = None, input_audio: Optional[Union[MediaFile, str, bytes]] = None, continuation_end: Optional[int] = None, **kwargs) -> APISeex:
        """
        
        
        
        Args:
            top_k: Reduces sampling to the k most likely tokens. Defaults to 250.
            
            top_p: Reduces sampling to tokens with cumulative probability of p. When set to  `0` (default), top_k sampling is used. Defaults to 0.0.
            
            duration: Duration of the generated audio in seconds. Defaults to 8.
            
            temperature: Controls the 'conservativeness' of the sampling process. Higher temperature means more diversity. Defaults to 1.0.
            
            continuation: If `True`, generated music will continue from `input_audio`. Otherwise, generated music will mimic `input_audio`'s melody. Defaults to False.
            
            output_format: Output format for generated audio. Defaults to 'wav'.
            
            continuation_start: Start time of the audio file to use for continuation. Defaults to 0.
            
            normalization_strategy: Strategy for normalizing audio. Defaults to 'loudness'.
            
            classifier_free_guidance: Increases the influence of inputs on the output. Higher values produce lower-varience outputs that adhere more closely to inputs. Defaults to 3.
            
            seed: Seed for random number generator. If None or -1, a random seed will be used. Optional.
            
            prompt: A description of the music you want to generate. Optional.
            
            input_audio: An audio file that will influence the generated music. If `continuation` is `True`, the generated music will be a continuation of the audio file. Otherwise, the generated music will mimic the audio file's melody. Optional.
            
            continuation_end: End time of the audio file to use for continuation. If -1 or None, will default to the end of the audio clip. Optional.
            
        """
        return self.submit_job("/predictions", top_k=top_k, top_p=top_p, duration=duration, temperature=temperature, continuation=continuation, output_format=output_format, continuation_start=continuation_start, normalization_strategy=normalization_strategy, classifier_free_guidance=classifier_free_guidance, seed=seed, prompt=prompt, input_audio=input_audio, continuation_end=continuation_end, **kwargs)
    
    # Convenience aliases for the primary endpoint
    run = predictions
    __call__ = predictions