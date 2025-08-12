"""
bilateral-truth - Caching Bilateral Factuality Evaluation

This package implements bilateral factuality evaluation using generalized truth values,
providing cached evaluation of assertions with support for multiple LLM evaluators.
"""

from .truth_values import GeneralizedTruthValue, TruthValueComponent, EpistemicPolicy
from .assertions import Assertion
from .zeta_function import zeta, zeta_c, clear_cache, get_cache_size
from .llm_evaluators import (
    LLMEvaluator,
    OpenAIEvaluator,
    AnthropicEvaluator,
    MockLLMEvaluator,
    create_llm_evaluator,
)
from .model_router import ModelRouter, OpenRouterEvaluator

__version__ = "0.2.0"
__all__ = [
    "GeneralizedTruthValue",
    "TruthValueComponent",
    "EpistemicPolicy",
    "Assertion",
    "zeta",
    "zeta_c",
    "clear_cache",
    "get_cache_size",
    "LLMEvaluator",
    "OpenAIEvaluator",
    "AnthropicEvaluator",
    "MockLLMEvaluator",
    "OpenRouterEvaluator",
    "create_llm_evaluator",
    "ModelRouter",
]
