# whisper_evaluator/model_wrapper.py
import torch
from transformers import pipeline

class WhisperModel:
    """
    A wrapper for the Hugging Face ASR pipeline for Whisper models.
    """
    def __init__(self, name_or_path: str, device: str = "cuda"):
        """
        Initializes the Whisper model using the Hugging Face pipeline.

        Args:
            name_or_path (str): The model ID on the Hub or path to a local model.
            device (str): The device to run the model on ('cuda' or 'cpu').
        """
        if device == "cuda" and not torch.cuda.is_available():
            print("Warning: CUDA not available, falling back to CPU.")
            resolved_device = "cpu"
        else:
            resolved_device = device

        # The pipeline handles model and processor loading, device placement,
        # and long audio chunking automatically.
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=name_or_path,
            device=resolved_device,
            chunk_length_s=30,
        )

    def transcribe(self, audio_array, sampling_rate: int) -> str:
        """
        Generates a transcription for a single audio input.

        Args:
            audio_array: The raw audio waveform as a NumPy array or list of floats.
            sampling_rate (int): The sampling rate of the audio.

        Returns:
            str: The transcribed text.
        """
        # The pipeline expects a dictionary with the raw audio and sampling rate.
        # It returns a dictionary, so we extract the 'text' key.
        result = self.pipe({"raw": audio_array, "sampling_rate": sampling_rate})
        return result["text"]