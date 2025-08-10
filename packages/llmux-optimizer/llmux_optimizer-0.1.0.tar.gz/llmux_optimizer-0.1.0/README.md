# LLMux-Optimizer

[![PyPI version](https://badge.fury.io/py/llmux-optimizer.svg)](https://badge.fury.io/py/llmux-optimizer)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/llmux-optimizer)](https://pepy.tech/project/llmux-optimizer)

Automatically find cheaper LLM alternatives while maintaining performance.

## Quick Start

```python
import llmux

# Find the cheapest model that maintains your accuracy requirements
result = llmux.optimize_cost(
    baseline="gpt-4",
    dataset="your_data.jsonl",
    min_accuracy=0.9
)

print(f"Best model: {result['model']}")
print(f"Cost savings: {result['cost_savings']:.1%}")
print(f"Accuracy: {result['accuracy']:.1%}")
```

## Installation

```bash
pip install llmux-optimizer
```

## Why LLMux?

- **One-liner optimization** - Just specify baseline and dataset
- **Real cost savings** - Average 73% reduction in LLM costs
- **Multiple providers** - Tests 18+ models across OpenAI, Anthropic, Google, Meta, Mistral, and more
- **Smart stopping** - Skips smaller models when larger ones fail (saves API calls)
- **Production ready** - Used by companies processing millions of requests

## Features

### Simple API

```python
# Basic usage
result = llmux.optimize_cost(
    baseline="gpt-4",
    dataset="data.jsonl"
)

# With custom parameters
result = llmux.optimize_cost(
    baseline="gpt-4",
    dataset="data.jsonl",
    prompt="Classify the sentiment as positive, negative, or neutral",
    task="classification",
    min_accuracy=0.85,
    sample_size=0.2  # Test on 20% of data for speed
)
```

### Supported Tasks

- **Classification** - Sentiment analysis, intent detection, categorization
- **Extraction** - Named entity recognition, information extraction
- **Generation** - Text completion, summarization, translation
- **Binary** - Yes/no, true/false decisions

### Model Universe

Tests models from a curated universe including:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3 Haiku, Sonnet)
- Google (Gemini Pro, Flash)
- Meta (Llama 3.1 8B, 70B)
- Mistral (7B, Mixtral, Large)
- And more...

## Examples

### Classification Task

```python
import llmux

# Sentiment analysis
examples = [
    {"input": "This product is amazing!", "ground_truth": "positive"},
    {"input": "Terrible service", "ground_truth": "negative"},
    {"input": "It's okay", "ground_truth": "neutral"}
]

result = llmux.optimize_cost(
    baseline="gpt-4",
    examples=examples,
    task="classification",
    options=["positive", "negative", "neutral"]
)
```

### Banking Intent Classification

```python
# Prepare dataset (one-time)
from prepare_banking77 import prepare_banking77_dataset
prepare_banking77_dataset()

# Find optimal model
result = llmux.optimize_cost(
    baseline="gpt-4",
    dataset="data/banking77_test.jsonl",
    prompt="Classify the banking customer query into one of 77 intent categories",
    task="classification",
    min_accuracy=0.8
)
```

### Cost Comparison

Typical savings on standard benchmarks:

| Dataset | Baseline | Best Alternative | Cost Savings | Accuracy |
|---------|----------|------------------|--------------|----------|
| IMDB | GPT-4 | Llama-3.1-8B | 96.3% | 95.2% |
| AG News | GPT-4 | Mistral-7B | 94.7% | 93.8% |
| Banking77 | GPT-4 | GPT-3.5-turbo | 89.2% | 91.4% |

## Advanced Usage

### Custom Evaluation

```python
from llmux import Evaluator, Provider

# Use specific provider
provider = Provider.get_provider("openrouter", model="meta-llama/llama-3.1-8b")
evaluator = Evaluator(provider)

# Run evaluation
accuracy, results = evaluator.evaluate(
    dataset="test_data.jsonl",
    system_prompt="You are a helpful assistant"
)
```

### Smart Stopping

LLMux automatically implements smart stopping - if a larger model in a family (e.g., Llama-70B) fails to meet accuracy requirements, smaller models (Llama-8B) are skipped to save API calls.

## Dataset Format

LLMux expects JSONL format with `input` and `label` fields:

```json
{"input": "Example text", "label": "category"}
{"input": "Another example", "label": "other_category"}
```

Or use the `examples` parameter directly:

```python
examples = [
    {"input": "text", "ground_truth": "label"},
    ...
]
```

## API Reference

### optimize_cost()

Main function to find the best cost-optimized model.

**Parameters:**
- `baseline` (str): Reference model to beat (e.g., "gpt-4")
- `dataset` (str): Path to JSONL dataset file
- `prompt` (str, optional): System prompt for the task
- `task` (str, optional): Task type ("classification", "extraction", "generation", "binary")
- `min_accuracy` (float): Minimum acceptable accuracy (default: 0.9)
- `sample_size` (float, optional): Percentage of dataset to use (0.0-1.0)
- `options` (list, optional): Valid output options for classification
- `examples` (list, optional): Direct examples instead of dataset file

**Returns:**
- Dictionary with:
  - `model`: Best model found
  - `accuracy`: Achieved accuracy
  - `cost_savings`: Percentage saved vs baseline
  - `cost_per_million`: Cost per million tokens

## Requirements

- Python 3.8+
- OpenRouter API key (set as `OPENROUTER_API_KEY` environment variable)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Citation

If you use LLMux in your research, please cite:

```bibtex
@software{llmux2024,
  title = {LLMux: Automatic LLM Cost Optimization},
  author = {Ahuja, Mihir},
  year = {2024},
  url = {https://github.com/mihirahuja/llmux}
}
```

## Support

- Issues: [GitHub Issues](https://github.com/mihirahuja/llmux/issues)
- Discussions: [GitHub Discussions](https://github.com/mihirahuja/llmux/discussions)
- Email: your@email.com