# whisper_evaluator/task.py
from datasets import load_dataset

class ASRTask:
    """
    Handles loading and preparing a dataset for Automatic Speech Recognition evaluation.
    """
    def __init__(self, dataset_name: str, dataset_subset: str, dataset_split: str, audio_column: str, text_column: str):
        """
        Initializes and loads the dataset from the Hugging Face Hub.

        Args:
            dataset_name (str): Name of the dataset on the Hub.
            dataset_subset (str): The configuration or subset of the dataset (e.g., language code).
            dataset_split (str): The split to use (e.g., 'test', 'validation').
            audio_column (str): The name of the column containing the audio data.
            text_column (str): The name of the column containing the reference transcription.
        """
        # Use the Hugging Face datasets library to load the data
        self.dataset = load_dataset(dataset_name, dataset_subset, split=dataset_split, trust_remote_code=True)

        # Standardize column names for the evaluator to use internally.
        # This makes the evaluator independent of the original dataset's schema.
        self.dataset = self.dataset.rename_columns({
            audio_column: "audio",
            text_column: "reference_text"
        })

    def __iter__(self):
        """Allows iterating directly over the processed dataset."""
        return iter(self.dataset)