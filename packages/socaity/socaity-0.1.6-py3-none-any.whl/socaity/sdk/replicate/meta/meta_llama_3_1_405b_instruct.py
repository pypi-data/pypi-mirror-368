from fastsdk import FastClient, APISeex
from typing import Optional


class meta_llama_3_1_405b_instruct(FastClient):
    """
    Generated client for meta/meta-llama-3-1-405b-instruct
    """
    def __init__(self, api_key: str = None):
        super().__init__(service_name_or_id="038ecce9-7616-4853-84c9-1a872f881d0c", api_key=api_key)
    
    def predictions(self, top_k: int = 50, top_p: float = 0.9, prompt: str = '', max_tokens: int = 512, min_tokens: int = 0, temperature: float = 0.6, system_prompt: str = 'You are a helpful assistant.', presence_penalty: float = 0.0, frequency_penalty: float = 0.0, stop_sequences: Optional[str] = None, **kwargs) -> APISeex:
        """
        
        
        
        Args:
            top_k: The number of highest probability tokens to consider for generating the output. If > 0, only keep the top k tokens with highest probability (top-k filtering). Defaults to 50.
            
            top_p: A probability threshold for generating the output. If < 1.0, only keep the top tokens with cumulative probability >= top_p (nucleus filtering). Nucleus filtering is described in Holtzman et al. (http://arxiv.org/abs/1904.09751). Defaults to 0.9.
            
            prompt: Prompt Defaults to ''.
            
            max_tokens: The maximum number of tokens the model should generate as output. Defaults to 512.
            
            min_tokens: The minimum number of tokens the model should generate as output. Defaults to 0.
            
            temperature: The value used to modulate the next token probabilities. Defaults to 0.6.
            
            system_prompt: System prompt to send to the model. This is prepended to the prompt and helps guide system behavior. Ignored for non-chat models. Defaults to 'You are a helpful assistant.'.
            
            presence_penalty: Presence penalty Defaults to 0.0.
            
            frequency_penalty: Frequency penalty Defaults to 0.0.
            
            stop_sequences: A comma-separated list of sequences to stop generation at. For example, '<end>,<stop>' will stop generation at the first instance of 'end' or '<stop>'. Optional.
            
        """
        return self.submit_job("/predictions", top_k=top_k, top_p=top_p, prompt=prompt, max_tokens=max_tokens, min_tokens=min_tokens, temperature=temperature, system_prompt=system_prompt, presence_penalty=presence_penalty, frequency_penalty=frequency_penalty, stop_sequences=stop_sequences, **kwargs)
    
    # Convenience aliases for the primary endpoint
    run = predictions
    __call__ = predictions