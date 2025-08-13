# AiDA Whisper Evaluation Framework (Serbian)


[An evaluation framework for Serbian Whisper models.](https://aida.guru)


# Whisper Evaluator 🎤

A simple, modular framework to evaluate fine-tuned Whisper models in Python notebooks.

This library allows you to easily run evaluations on any dataset from the Hugging Face Hub using a simple configuration dictionary. It calculates a comprehensive set of metrics, including WER, CER, BLEU, and ROUGE, and automatically logs all results to a file.

## Installation

You can install the library directly from GitHub:

```bash
pip install git+[https://github.com/your-username/whisper-evaluator.git](https://github.com/your-username/whisper-evaluator.git)
```

## Quickstart

Using the library in a Google Colab or Jupyter Notebook is straightforward.

```python
from whisper_evaluator import Evaluator
import json

# 1. Define your evaluation configuration
config = {
    "model_args": {
        "name_or_path": "openai/whisper-large-v2", # Your fine-tuned model ID
        "device": "cuda"
    },
    "task_args": {
        "dataset_name": "mozilla-foundation/common_voice_11_0",
        "dataset_subset": "sr", # Serbian language
        "dataset_split": "test[:20]", # Use the first 20 samples for a quick demo
        "audio_column": "audio",
        "text_column": "sentence"
    }
}

# 2. Initialize the evaluator
evaluator = Evaluator(config=config)

# 3. Run the evaluation (logs to 'evaluation_log.txt' by default)
detailed_results, metrics = evaluator.run()

# 4. Analyze the results
print("\n--- Final Metrics ---")
# Pretty print the metrics dictionary
print(json.dumps(metrics, indent=2))

print("\n--- Sample of evaluation details ---")
# Print the first 3 results from the list
for i, result in enumerate(detailed_results[:3]):
    print(f"\n--- Example {i+1} ---")
    print(f"Reference:  {result['reference']}")
    print(f"Prediction: {result['prediction']}")
```







# Project Setup

Follow these steps to set up the **AiDA-Whisper-Eval** project.

---

### Using Conda

### 1. Create a new Conda environment

```bash
conda create --name aida python=3.12 -y
conda activate aida
```

#### 2. Install Poetry

```bash
pip install poetry
```

#### 3. Install project dependencies

Navigate to the project's root directory and run:

```bash
poetry install
```

---

### Using Plain Python

#### 1. Create and activate a virtual environment

```bash
python -m venv venv

# On Linux/macOS
source venv/bin/activate

# On Windows
.\venv\Scripts\activate
```

#### 2. Upgrade pip and install Poetry

```bash
pip install --upgrade pip
pip install poetry
```

#### 3. Install project dependencies

From the project's root directory, run:

```bash
poetry install
```

```bash
pip install pre-commit
```

### 4. Set up pre-commit hooks

```bash
poetry run pre-commit install
```

---

### Verifying Installation

Check installation by running tests:

```bash
# On Linux/macOS
make test

# On Windows
poetry run pytest
```

Your setup is complete!
