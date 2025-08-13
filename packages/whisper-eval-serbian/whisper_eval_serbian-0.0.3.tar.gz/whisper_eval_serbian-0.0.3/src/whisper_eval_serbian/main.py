def hello():
    print("Hello, World!") 

from whisper_eval_serbian.evaluator import Evaluator
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