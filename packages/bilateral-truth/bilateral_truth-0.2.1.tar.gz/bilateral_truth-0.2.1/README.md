# bilateral-truth: Caching Bilateral Factuality Evaluation

A Python package for bilateral factuality evaluation with generalized truth values and persistent caching.

## Overview

This package implements the mathematical function:

**ζ_c: ℒ_AT → 𝒱³ × 𝒱³**

Where:
- ℒ_AT is the language of assertions
- 𝒱³ represents 3-valued logic components {t, e, f} (true, undefined, false)
- The function returns generalized truth values <u,v> with bilateral evaluation

## Key Features

- **Bilateral Evaluation**: Each assertion receives a generalized truth value <u,v> where u represents verifiability and v represents refutability
- **Persistent Caching**: The evaluation function maintains a cache to avoid recomputing truth values for previously evaluated assertions
- **3-Valued Logic**: Supports true (t), undefined (e), and false (f) truth value components
- **Extensible Evaluation**: Custom evaluation functions can be provided for domain-specific logic

## Installation

### From PyPI (Recommended)

```bash
# Core package with mock evaluator
pip install bilateral-truth

# With OpenAI support
pip install bilateral-truth[openai]

# With Anthropic (Claude) support  
pip install bilateral-truth[anthropic]

# With all LLM providers
pip install bilateral-truth[all]
```

### Development Setup

#### Option 1: Automated Setup (Recommended)

```bash
# Set up virtual environment and install everything
./setup_venv.sh

# Activate the virtual environment
source venv/bin/activate
```

#### Option 2: Manual Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the package in development mode with all dependencies
pip install -e .[all,dev]
```

## Quick Start

```python
from bilateral_truth import Assertion, zeta_c, create_llm_evaluator

# Create an LLM evaluator (requires API key)
evaluator = create_llm_evaluator('openai', model='gpt-4')
# or: evaluator = create_llm_evaluator('anthropic', model='claude-sonnet-4-20250514')
# or: evaluator = create_llm_evaluator('mock')  # for testing

# Create assertions
assertion1 = Assertion("The capital of France is Paris")
assertion2 = Assertion("loves", "alice", "bob") 
assertion3 = Assertion("It will rain tomorrow")

# Evaluate using ζ_c with LLM-based bilateral assessment
result1 = zeta_c(assertion1, evaluator.evaluate_bilateral)
result2 = zeta_c(assertion2, evaluator.evaluate_bilateral)
result3 = zeta_c(assertion3, evaluator.evaluate_bilateral)

print(f"zeta_c({assertion1}) = {result1}")
print(f"zeta_c({assertion2}) = {result2}")
print(f"zeta_c({assertion3}) = {result3}")
```

## Core Components

### Generalized Truth Values

```python
from bilateral_truth import GeneralizedTruthValue, TruthValueComponent

# Classical values using projection
from bilateral_truth import EpistemicPolicy

classical_true = GeneralizedTruthValue(TruthValueComponent.TRUE, TruthValueComponent.FALSE)   # <t,f>
classical_false = GeneralizedTruthValue(TruthValueComponent.FALSE, TruthValueComponent.TRUE) # <f,t>
undefined_val = GeneralizedTruthValue(TruthValueComponent.UNDEFINED, TruthValueComponent.UNDEFINED) # <e,e>

# Project to 3-valued logic
projected_true = classical_true.project(EpistemicPolicy.CLASSICAL)    # t
projected_false = classical_false.project(EpistemicPolicy.CLASSICAL)  # f
projected_undefined = undefined_val.project(EpistemicPolicy.CLASSICAL) # e

# Custom combinations
custom_val = GeneralizedTruthValue(
    TruthValueComponent.TRUE,
    TruthValueComponent.UNDEFINED
)  # <t,e>
```

### Assertions

```python
from bilateral_truth import Assertion

# Simple statement
statement = Assertion("The sky is blue")

# Predicate with arguments  
loves = Assertion("loves", "alice", "bob")

# With named arguments
distance = Assertion("distance", 
                        start="NYC", 
                        end="LA", 
                        value=2500, 
                        unit="miles")

# Natural language statements
weather = Assertion("It will rain tomorrow")
fact = Assertion("The capital of France is Paris")
```

### Caching Behavior

The zeta_c function implements the mathematical definition:

```
zeta_c(φ) = {
  c(φ)   if φ ∈ dom(c)
  ζ(φ)   otherwise, and c := c ∪ {(φ, ζ(φ))}
}
```

```python
from bilateral_truth import zeta_c, get_cache_size, clear_cache

assertion = Assertion("test")

# First evaluation computes and caches
result1 = zeta_c(assertion)
print(f"Cache size: {get_cache_size()}")  # 1

# Second evaluation uses cache
result2 = zeta_c(assertion)
print(f"Same result: {result1 == result2}")  # True
print(f"Cache size: {get_cache_size()}")  # Still 1
```

### LLM-Based Bilateral Evaluation

```python
# Set up environment variables first:
# export OPENAI_API_KEY='your-key'
# export ANTHROPIC_API_KEY='your-key'

from bilateral_truth import zeta_c, create_llm_evaluator, Assertion

# Create real LLM evaluator  
openai_evaluator = create_llm_evaluator('openai', model='gpt-4')
claude_evaluator = create_llm_evaluator('anthropic')

# Or use mock evaluator for testing/development
mock_evaluator = create_llm_evaluator('mock')

# The LLM will assess both verifiability and refutability
assertion = Assertion("The Earth is round")
result = zeta_c(assertion, openai_evaluator.evaluate_bilateral)

# The LLM receives a prompt asking it to evaluate:
# 1. Can this statement be verified as true? (verifiability)  
# 2. Can this statement be refuted as false? (refutability)
# And returns a structured <u,v> response
```

## API Reference

### Functions

- **`zeta(assertion, evaluator)`**: Base bilateral evaluation function (requires LLM evaluator)
- **`zeta_c(assertion, evaluator, cache=None)`**: Cached bilateral evaluation function
- **`clear_cache()`**: Clear the global cache
- **`get_cache_size()`**: Get the number of cached entries
- **`create_llm_evaluator(provider, **kwargs)`**: Factory for creating LLM evaluators

### Classes

- **`Assertion(statement, *args, **kwargs)`**: Represents natural language assertions or predicates
- **`GeneralizedTruthValue(u, v)`**: Represents <u,v> truth values
- **`TruthValueComponent`**: Enum for t, e, f values
- **`ZetaCache`**: Cache implementation for zeta_c
- **`OpenAIEvaluator`**: LLM evaluator using OpenAI's API
- **`AnthropicEvaluator`**: LLM evaluator using Anthropic's API
- **`MockLLMEvaluator`**: Mock evaluator for testing/development

## Command Line Interface

After installation, use the `bilateral-truth` command:

```bash
# Install the package first
pip install -e .

# Interactive mode with GPT-4 (requires OPENAI_API_KEY)
bilateral-truth --model gpt-4 --interactive

# Single assertion evaluation with Claude (requires ANTHROPIC_API_KEY)
bilateral-truth --model claude "The capital of France is Paris"

# Use OpenRouter with Llama model (requires OPENROUTER_API_KEY)
bilateral-truth --model llama3-70b "Climate change is real"

# Use mock model for testing (no API key needed)
bilateral-truth --model mock "The sky is blue"

# Use majority voting with 5 samples for more robust results
bilateral-truth --model gpt-4 --samples 5 "Climate change is real"

# Use pessimistic tiebreaking with even number of samples
bilateral-truth --model claude --samples 4 --tiebreak pessimistic "The Earth is round"

# List all available models
bilateral-truth --list-models

# Get information about a specific model
bilateral-truth --model-info gpt-4
```

### Running without installation:

```bash
# Use the standalone script
python cli.py -m mock "The Earth is round"

# Interactive mode with sampling
python cli.py -m mock -s 3 --tiebreak random -i

# Single evaluation with majority voting
python cli.py -m llama3 -s 5 "The sky is blue"

# Run the demo
python demo_cli.py
```

### Supported Models

The CLI supports models from multiple providers:

- **OpenAI**: GPT-4, GPT-3.5-turbo, etc.
- **Anthropic**: Claude-4 (Opus, Sonnet)
- **OpenRouter**: Llama, Mistral, Gemini, and many more models
- **Mock**: For testing and development

### API Keys

Set environment variables for the providers you want to use:

```bash
export OPENAI_API_KEY='your-openai-key'
export ANTHROPIC_API_KEY='your-anthropic-key'
export OPENROUTER_API_KEY='your-openrouter-key'
```

### Sampling and Majority Voting

The CLI supports robust evaluation using multiple samples and majority voting, as described in the ArXiv paper:

```bash
# Single evaluation (default)
python cli.py -m gpt4 "The sky is blue"

# Majority voting with 5 samples for more robust results
python cli.py -m gpt4 -s 5 "Climate change is real"

# Even number of samples with tiebreaking strategies
python cli.py -m claude -s 4 --tiebreak conservative "The Earth is round"
python cli.py -m llama3 -s 6 --tiebreak optimistic "AI will be beneficial"
python cli.py -m mixtral -s 4 --tiebreak random "Democracy is good"
```

**Tiebreaking Strategies:**

When multiple samples produce tied votes for a component, the tiebreaking strategy determines the outcome:

- **`random`** (default): Randomly choose among tied components
  - Unbiased but unpredictable
  - Example: `[t,t,f,f]` → randomly pick `t` or `f`

- **`pessimistic`**: Prefer `f` (cannot verify/refute) when in doubt
  - Bias toward epistemic caution: "Better to admit uncertainty than make false claims"
  - Tends toward `<f,f>` (paracomplete/unknown) outcomes
  - Example: `[t,t,f,f]` → choose `f`

- **`optimistic`**: Prefer `t` (verified/refuted) when in doubt  
  - Bias toward strong claims: "Give statements the benefit of the doubt"
  - Tends toward classical `<t,f>` or `<f,t>` outcomes
  - Example: `[t,t,f,f]` → choose `t`

**Benefits of Sampling:**
- Reduces variance in LLM responses
- More reliable bilateral evaluation results
- Configurable confidence through sample size
- Handles ties systematically with multiple strategies

## Examples

Run the included examples:

```bash
python llm_examples.py    # LLM-based bilateral evaluation examples
python examples.py        # Legacy examples (deprecated)
python demo_cli.py        # CLI demonstration
```

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

Or run individual test modules:

```bash
python -m unittest tests.test_truth_values
python -m unittest tests.test_assertions
python -m unittest tests.test_zeta_function
```

## Mathematical Background

This implementation is based on bilateral factuality evaluation as described in the research paper. The key mathematical concepts include:

1. **Generalized Truth Values**: <u,v> pairs where both components are from {t, e, f} where:
   - First position (u): t = verifiable, f = not verifiable, e = undefined
   - Second position (v): t = refutable, f = not refutable, e = undefined
2. **Bilateral Evaluation**: Separate assessment of verifiability (u) and refutability (v)
3. **Persistent Caching**: Immutable cache updates maintaining consistency across evaluations

## Requirements

- Python 3.9+
- No external dependencies (uses only Python standard library)

## License

MIT License

## Citation

If you use this implementation in research, please cite the original paper:
[ArXiv Paper Link](https://arxiv.org/html/2507.09751v2)