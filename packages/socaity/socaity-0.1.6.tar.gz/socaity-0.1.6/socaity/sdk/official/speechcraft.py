from fastsdk import FastClient, APISeex
from typing import Union, Any

from media_toolkit import AudioFile, MediaFile


class speechcraft(FastClient):
    """
    Create audio from text, clone voices and use them. Convert voice2voice. Generative text-to-audio Bark model.
    """
    def __init__(self, api_key: str = None):
        super().__init__(service_name_or_id="ee0af319-70d4-4171-9954-c24ad01b3e05", api_key=api_key)
    
    def text2voice(self, text: str, voice: Union[Any, MediaFile, str, bytes] = 'en_speaker_3', fine_temp: float = 0.5, coarse_temp: float = 0.7, coarse_top_k: int = 50, coarse_top_p: float = 0.95, semantic_temp: float = 0.7, semantic_top_k: int = 50, semantic_top_p: float = 0.95, **kwargs) -> APISeex:
        """
        :param text: the text to be converted
        :param voice: the name of the voice to be used. Uses the pretrained voices which are stored in models/speakers folder.
            It is also possible to provide a full path.
        :return: the audio file as bytes
        
        """
        return self.submit_job("/text2voice", text=text, voice=voice, fine_temp=fine_temp, coarse_temp=coarse_temp, coarse_top_k=coarse_top_k, coarse_top_p=coarse_top_p, semantic_temp=semantic_temp, semantic_top_k=semantic_top_k, semantic_top_p=semantic_top_p, **kwargs)
    
    def voice2voice(self, audio_file: Union[AudioFile, Any, MediaFile, str, bytes], temp: float = 0.7, voice_name: Union[Any, MediaFile, str, bytes] = 'en_speaker_3', **kwargs) -> APISeex:
        """
        :param audio_file: the audio file as bytes 5-20s is good length
        :param voice_name: the new of the voice to convert to; or the voice embedding. String or MediaFile.
        :param temp: generation temperature (1.0 more diverse, 0.0 more conservative)
        :return: the converted audio file as bytes
        
        """
        return self.submit_job("/voice2voice", audio_file=audio_file, temp=temp, voice_name=voice_name, **kwargs)
    
    def voice2embedding(self, audio_file: Union[AudioFile, Any, MediaFile, str, bytes], save: bool = False, voice_name: str = 'new_speaker', **kwargs) -> APISeex:
        """
        :param audio_file: the audio file as bytes 5-20s is good length
        :param voice_name: how the new voice / embedding is named
        :param save: if the embedding should be saved in the voice dir for reusage.
            Note: depending on the server settings this might not be allowed
        :return: the voice embedding as bytes
        
        """
        return self.submit_job("/voice2embedding", audio_file=audio_file, save=save, voice_name=voice_name, **kwargs)
    
    # Convenience aliases for the primary endpoint
    run = text2voice
    __call__ = text2voice