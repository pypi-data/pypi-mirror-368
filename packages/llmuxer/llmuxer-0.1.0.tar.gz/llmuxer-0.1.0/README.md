# LLMuxer

[![PyPI version](https://badge.fury.io/py/llmuxer.svg)](https://pypi.org/project/llmuxer/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI Tests](https://github.com/mihirahuja1/llmuxer/workflows/CI/badge.svg)](https://github.com/mihirahuja1/llmuxer/actions)
[![Coverage](https://codecov.io/gh/mihirahuja1/llmuxer/branch/main/graph/badge.svg)](https://codecov.io/gh/mihirahuja1/llmuxer)
[![Downloads](https://pepy.tech/badge/llmuxer)](https://pepy.tech/project/llmuxer)
[![GitHub Stars](https://img.shields.io/github/stars/mihirahuja1/llmuxer)](https://github.com/mihirahuja1/llmuxer/stargazers)

**Find the cheapest LLM that meets your quality bar** *(Currently supports classification tasks only)*

## Quick Start

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/mihirahuja1/llmuxer/blob/main/examples/quickstart.ipynb)

```python
import llmuxer

# Example: Classify sentiment with 90% accuracy requirement
examples = [
    {"input": "This product is amazing!", "label": "positive"},
    {"input": "Terrible service", "label": "negative"},
    {"input": "It's okay", "label": "neutral"}
]

result = llmuxer.optimize_cost(
    baseline="gpt-4",
    examples=examples,
    task="classification",  # Currently only classification is supported
    options=["positive", "negative", "neutral"],
    min_accuracy=0.9  # Require 90% accuracy
)

print(result)
# Takes ~30-60 seconds for small datasets, ~10-15 minutes for 1k samples
```

### Example Output
```python
{
    "model": "anthropic/claude-3-haiku",
    "accuracy": 0.92,
    "cost_per_million": 0.25,
    "cost_savings": 0.975,  # 97.5% cheaper than GPT-4
    "baseline_cost_per_million": 10.0,
    "tokens_evaluated": 1500
}
```

## The Problem

You're using GPT-4 for classification. It works well but costs $20/million tokens. Could GPT-3.5 do just as well for $0.50? What about Claude Haiku at $0.25? Or Llama-3.1 at $0.06?

**LLMuxer automatically tests your classification task across 18 models to find the cheapest one that maintains your required accuracy.**

## How It Works

```
Your Dataset → LLMuxer → Tests 18 Models → Returns Cheapest That Works
                  ↓
           Uses OpenRouter API
           (unified interface)
```

LLMuxer:
1. Takes your baseline model (e.g., GPT-4) and test dataset
2. Evaluates cheaper alternatives via OpenRouter
3. Returns the cheapest model meeting your accuracy threshold
4. Shows detailed cost breakdown and savings

## Installation

### Prerequisites
- Python 3.8+
- [OpenRouter API key](https://openrouter.ai/keys) (for model access)

### Install
```bash
pip install llmuxer
```

### Setup
```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

## Key Features

- **18 models tested** - OpenAI, Anthropic, Google, Meta, Mistral, Qwen, DeepSeek  
- **Smart stopping** - Skips smaller models if larger ones fail  
- **Cost breakdown** - See token counts and costs per model  
- **Fast testing** - Use `sample_size` to test on subset first  
- **Simple API** - One function does everything  
- **Classification only** - Support for extraction, generation, and binary tasks coming in v0.2

## Benchmarks

### Tested Models

*Live pricing data from OpenRouter API (updated automatically):*

| Provider | Models | Price Range ($/M tokens) |
|----------|--------|--------------------------|
| OpenAI | gpt-4o-mini, gpt-3.5-turbo | $0.75 - $2.00 |
| Anthropic | claude-3-haiku | $1.50 |
| DeepSeek | deepseek-chat | $0.90 |
| Mistral | 3 models | $0.08 - $8.00 |
| Meta | llama-3.1-8b-instruct, llama-3.1-70b-instruct | $0.04 - $0.38 |

**Total: 9 models across 5 providers**

### Reproduce Our Benchmarks

```bash
# Test all 9 models on Banking77 dataset
python scripts/prepare_banking77.py
python examples/banking77_test.py
```

**Expected Results:** Most models achieve 85-92% accuracy on Banking77. Claude-3-haiku typically provides the best accuracy/cost ratio for classification tasks.

### Performance Benchmarks

**Fixed Dataset Results** *(50 job classification samples, tested 2025-08-10)*

| Metric | Baseline (GPT-4o) | Best Model (Claude-3-haiku) | Savings |
|--------|------------------|---------------------------|---------|
| **Accuracy** | ~95% (assumed) | **92.0%** | Quality maintained |
| **Cost/Million Tokens** | $12.50 | **$1.50** | **88.0% cheaper** |
| **Cost/Request*** | $0.001875 | **$0.000225** | **$0.00165 saved** |
| **Monthly (1K requests)** | $1.88 | **$0.23** | **$1.65 saved** |

*Conservative estimate: 150 tokens/request (100 input + 50 output)*

**[📊 Full Benchmark Report](docs/benchmarks.md)** | **[🔄 Reproduction Guide](#reproduction)**

### Reproduction

```bash
# Install and setup
pip install llmuxer
export OPENROUTER_API_KEY="your-key"

# Run exact benchmark  
./scripts/bench.sh

# Generates: benchmarks/bench_YYYYMMDD.json + docs/benchmarks.md
```

**Benchmark Notes:**
- Fixed dataset: `data/jobs_50.jsonl` (8 categories, 50 samples)
- Pinned models: 8 specific models with exact API versions  
- Conservative estimates: 150 tokens/request assumption
- No cherry-picking: Single test run results
- Quality threshold: 85%+ accuracy required

## API Reference

### `optimize_cost()`

Find the cheapest model meeting your requirements for classification tasks.

**Parameters:**
- `baseline` (str): Your current model (e.g., "gpt-4")
- `examples` (list): Test examples with input and label
- `dataset` (str): Path to JSONL file (alternative to examples)
- `task` (str): Must be "classification" (other tasks coming soon)
- `options` (list): Valid output classes for classification
- `min_accuracy` (float): Minimum acceptable accuracy (0.0-1.0)
- `sample_size` (float): Fraction of dataset to test (0.0-1.0)
- `prompt` (str): Optional system prompt

**Returns:**
Dictionary with model name, accuracy, cost, and savings.

**Error Handling:**
- Returns `{"error": "message"}` if no model meets threshold
- Retries on API failures
- Validates dataset format

## Full Example: Banking Intent Classification

```python
import llmuxer

# Using the Banking77 dataset (77 intent categories)
result = llmuxer.optimize_cost(
    baseline="gpt-4",
    dataset="data/banking77.jsonl",  # Your prepared dataset
    task="classification",
    min_accuracy=0.8,
    sample_size=0.2  # Test on 20% first for speed
)

if "error" in result:
    print(f"No model found: {result['error']}")
else:
    print(f"Switch from {baseline} to {result['model']}")
    print(f"Save {result['cost_savings']:.0%} on costs")
    print(f"Accuracy: {result['accuracy']:.1%}")
```

## Dataset Format

JSONL format with `input` and `label` fields:
```json
{"input": "What's my account balance?", "label": "balance_inquiry"}
{"input": "I lost my card", "label": "card_lost"}
```

## Performance Notes

### Timing Estimates

For a dataset with 1,000 samples:

| Model Type | Time per 1k samples | Token Speed |
|------------|-------------------|-------------|
| GPT-3.5-turbo | ~45-60 seconds | ~2,000 tokens/sec |
| Claude-3-haiku | ~30-45 seconds | ~2,500 tokens/sec |
| Gemini-1.5-flash | ~20-30 seconds | ~3,000 tokens/sec |
| Llama-3.1-8b | ~15-25 seconds | ~3,500 tokens/sec |
| **Total for 18 models** | **~10-15 minutes** | Sequential |

### Speed Considerations

- **Sequential Processing**: Currently tests one model at a time (parallel in v0.2)
- **Sample Size**: Use `sample_size=0.1` to test on 10% first for quick validation
- **Smart Stopping**: Saves 30-50% time by skipping smaller models when larger ones fail
- **Rate Limits**: Automatic handling with exponential backoff
- **Caching**: Not yet implemented (coming in v0.2 will reduce re-evaluation time by 90%)

## Links

- [PyPI Package](https://pypi.org/project/llmuxer/)
- [GitHub Repository](https://github.com/mihirahuja1/llmuxer)
- [OpenRouter API Keys](https://openrouter.ai/keys)
- [Full Documentation](https://github.com/mihirahuja1/llmuxer/tree/main/docs)
- [Roadmap](https://github.com/mihirahuja1/llmuxer/blob/main/ROADMAP.md)

## License

MIT - see [LICENSE](LICENSE) file.

## Support

- Issues: [GitHub Issues](https://github.com/mihirahuja1/llmuxer/issues)
- Email: mihirahuja09@gmail.com