"""
Model routing functionality for the ζ_c CLI.

This module provides routing logic to determine which LLM provider and
configuration to use based on model names, including OpenRouter support.
"""

import re
from typing import Dict, Tuple, Optional, TYPE_CHECKING
from .llm_evaluators import (
    LLMEvaluator,
    OpenAIEvaluator,
    AnthropicEvaluator,
    MockLLMEvaluator,
)

if TYPE_CHECKING:
    from .assertions import Assertion
    from .truth_values import GeneralizedTruthValue, TruthValueComponent


class ModelRouter:
    """
    Routes model names to appropriate LLM evaluators and configurations.
    """

    # Model name patterns and their corresponding providers
    MODEL_PATTERNS = {
        # OpenAI models
        "openai": {
            "patterns": [
                r"^gpt-4.*",
                r"^gpt-3\.5.*",
                r"^text-davinci.*",
                r"^openai/.*",
            ],
            "provider": "openai",
            "default_model": "gpt-4",
        },
        # Anthropic models
        "anthropic": {
            "patterns": [
                r"^claude-.*-4.*",
                r"^claude-sonnet.*",
                r"^claude-opus.*",
                r"^anthropic/.*",
            ],
            "provider": "anthropic",
            "default_model": "claude-sonnet-4-20250514",
        },
        # OpenRouter models (supports many providers)
        "openrouter": {
            "patterns": [
                r"^openrouter/.*",
                r"^meta-llama/.*",
                r"^mistralai/.*",
                r"^google/.*",
                r"^cohere/.*",
                r"^perplexity/.*",
                r"^nousresearch/.*",
                r"^microsoft/.*",
                r"^01-ai/.*",
            ],
            "provider": "openrouter",
            "default_model": "openrouter/auto",
        },
        # Mock models for testing
        "mock": {
            "patterns": [r"^mock.*", r"^test.*", r"^demo.*"],
            "provider": "mock",
            "default_model": "mock",
        },
    }

    # Aliases for common model names
    MODEL_ALIASES = {
        # OpenAI aliases
        "gpt4": "gpt-4",
        "gpt-4-turbo": "gpt-4-turbo-preview",
        "gpt3.5": "gpt-3.5-turbo",
        "gpt35": "gpt-3.5-turbo",
        # Anthropic aliases
        "claude": "claude-sonnet-4-20250514",
        "claude4": "claude-sonnet-4-20250514",
        "claude-sonnet": "claude-sonnet-4-20250514",
        "claude-opus": "claude-opus-4-20250514",
        # OpenRouter aliases
        "llama": "meta-llama/llama-3.1-8b-instruct",
        "llama3": "meta-llama/llama-3.1-8b-instruct",
        "llama3-70b": "meta-llama/llama-3.1-70b-instruct",
        "mistral": "mistralai/mistral-7b-instruct",
        "mixtral": "mistralai/mixtral-8x7b-instruct",
        "gemini": "google/gemini-pro",
        "auto": "openrouter/auto",
        # Mock aliases
        "mock": "mock",
        "test": "mock",
        "demo": "mock",
    }

    @classmethod
    def resolve_model_name(cls, model_name: str) -> str:
        """
        Resolve model name aliases to canonical names.

        Args:
            model_name: The input model name (may be an alias)

        Returns:
            The canonical model name
        """
        # Convert to lowercase for case-insensitive matching
        normalized_name = model_name.lower().strip()

        # Check if it's an alias
        if normalized_name in cls.MODEL_ALIASES:
            return cls.MODEL_ALIASES[normalized_name]

        return model_name

    @classmethod
    def get_provider_info(cls, model_name: str) -> Tuple[str, str]:
        """
        Determine the provider and canonical model name for a given model.

        Args:
            model_name: The model name to route

        Returns:
            Tuple of (provider, canonical_model_name)

        Raises:
            ValueError: If the model name is not recognized
        """
        # First resolve any aliases
        resolved_name = cls.resolve_model_name(model_name)

        # Try to match against patterns
        for provider_name, config in cls.MODEL_PATTERNS.items():
            for pattern in config["patterns"]:
                if re.match(pattern, resolved_name, re.IGNORECASE):
                    return config["provider"], resolved_name

        # If no pattern matches, try exact matching with known models
        known_models = {
            # OpenAI models
            "gpt-4",
            "gpt-4-turbo-preview",
            "gpt-4-0125-preview",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0125",
            # Anthropic models
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514",
            # Mock models
            "mock",
        }

        if resolved_name in known_models:
            # Try to infer provider from model name
            if "gpt" in resolved_name or "davinci" in resolved_name:
                return "openai", resolved_name
            elif "claude" in resolved_name:
                return "anthropic", resolved_name
            elif resolved_name == "mock":
                return "mock", resolved_name

        raise ValueError(
            f"Unknown model: {model_name}. Supported models include GPT-4, Claude-4, OpenRouter models, or 'mock' for testing."
        )

    @classmethod
    def create_evaluator(cls, model_name: str, **kwargs) -> LLMEvaluator:
        """
        Create an LLM evaluator for the specified model.

        Args:
            model_name: The model name to create an evaluator for
            **kwargs: Additional arguments passed to the evaluator constructor

        Returns:
            An LLMEvaluator instance configured for the specified model

        Raises:
            ValueError: If the model name is not recognized
        """
        provider, canonical_model = cls.get_provider_info(model_name)

        if provider == "openai":
            return OpenAIEvaluator(model=canonical_model, **kwargs)
        elif provider == "anthropic":
            return AnthropicEvaluator(model=canonical_model, **kwargs)
        elif provider == "openrouter":
            return OpenRouterEvaluator(model=canonical_model, **kwargs)
        elif provider == "mock":
            return MockLLMEvaluator(**kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    @classmethod
    def list_available_models(cls) -> Dict[str, list]:
        """
        Get a list of available models organized by provider.

        Returns:
            Dictionary mapping provider names to lists of available models
        """
        return {
            "openai": [
                "gpt-4",
                "gpt-4-turbo-preview",
                "gpt-4-0125-preview",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-0125",
            ],
            "anthropic": [
                "claude-sonnet-4-20250514",
                "claude-opus-4-20250514",
            ],
            "openrouter": [
                "openrouter/auto",
                "meta-llama/llama-3.1-8b-instruct",
                "meta-llama/llama-3.1-70b-instruct",
                "mistralai/mistral-7b-instruct",
                "mistralai/mixtral-8x7b-instruct",
                "google/gemini-pro",
                "cohere/command-r-plus",
                "perplexity/llama-3.1-sonar-large-128k-online",
                "nousresearch/hermes-3-llama-3.1-405b",
                "microsoft/wizardlm-2-8x22b",
            ],
            "mock": ["mock"],
        }

    @classmethod
    def list_aliases(cls) -> Dict[str, str]:
        """
        Get a list of model aliases and their canonical names.

        Returns:
            Dictionary mapping aliases to canonical model names
        """
        return cls.MODEL_ALIASES.copy()


class OpenRouterEvaluator(LLMEvaluator):
    """LLM evaluator using OpenRouter's API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "openrouter/auto"):
        """
        Initialize OpenRouter evaluator.

        Args:
            api_key: OpenRouter API key. If None, reads from OPENROUTER_API_KEY environment variable
            model: Model name to use (default: openrouter/auto)
        """
        import os

        try:
            import openai
        except ImportError:
            raise ImportError(
                "openai package is required for OpenRouter. Install with: pip install openai"
            )

        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key must be provided or set in OPENROUTER_API_KEY environment variable"
            )

        self.model = model
        # OpenRouter uses OpenAI-compatible API
        self.client = openai.OpenAI(
            api_key=self.api_key, base_url="https://openrouter.ai/api/v1"
        )

    def evaluate_bilateral(
        self, assertion: "Assertion", samples: int = 1
    ) -> "GeneralizedTruthValue":
        """Evaluate assertion using OpenRouter API with optional sampling."""
        if samples > 1:
            return self.evaluate_with_majority_voting(assertion, samples)
        return self._single_evaluation(assertion)

    def _evaluate_verification(self, assertion: "Assertion") -> "TruthValueComponent":
        """Evaluate verification using OpenRouter API."""
        try:
            prompt = self._create_verification_prompt(assertion)

            # Build request parameters
            request_params = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert in factual verification. You must respond with only the exact required token sequences.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "max_completion_tokens": 10,  # Only need a few tokens for response
            }

            # Add temperature only for models that support it (some newer models don't support temperature=0.0)
            if not (self.model.startswith("gpt-5") or "gpt-5" in self.model):
                request_params["temperature"] = (
                    0.0  # Zero temperature for consistent token responses
                )

            response = self.client.chat.completions.create(**request_params)

            response_text = response.choices[0].message.content
            return self._parse_verification_response(response_text)

        except Exception as e:
            print(f"Warning: OpenRouter verification call failed: {e}")
            from .truth_values import TruthValueComponent

            return TruthValueComponent.UNDEFINED

    def _evaluate_refutation(self, assertion: "Assertion") -> "TruthValueComponent":
        """Evaluate refutation using OpenRouter API."""
        try:
            prompt = self._create_refutation_prompt(assertion)

            # Build request parameters
            request_params = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert in logical refutation. You must respond with only the exact required token sequences.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "max_completion_tokens": 10,  # Only need a few tokens for response
            }

            # Add temperature only for models that support it (some newer models don't support temperature=0.0)
            if not (self.model.startswith("gpt-5") or "gpt-5" in self.model):
                request_params["temperature"] = (
                    0.0  # Zero temperature for consistent token responses
                )

            response = self.client.chat.completions.create(**request_params)

            response_text = response.choices[0].message.content
            return self._parse_refutation_response(response_text)

        except Exception as e:
            print(f"Warning: OpenRouter refutation call failed: {e}")
            from .truth_values import TruthValueComponent

            return TruthValueComponent.UNDEFINED


def get_model_info(model_name: str) -> str:
    """
    Get information about a specific model.

    Args:
        model_name: The model name to get information for

    Returns:
        A string with information about the model
    """
    try:
        provider, canonical_name = ModelRouter.get_provider_info(model_name)

        info = f"Model: {canonical_name}\n"
        info += f"Provider: {provider}\n"

        if canonical_name != model_name:
            info += f"Resolved from: {model_name}\n"

        # Add provider-specific information
        if provider == "openai":
            info += "API Key: Set OPENAI_API_KEY environment variable\n"
            info += "Documentation: https://platform.openai.com/docs/models\n"
        elif provider == "anthropic":
            info += "API Key: Set ANTHROPIC_API_KEY environment variable\n"
            info += "Documentation: https://docs.anthropic.com/claude/docs/models-overview\n"
        elif provider == "openrouter":
            info += "API Key: Set OPENROUTER_API_KEY environment variable\n"
            info += "Documentation: https://openrouter.ai/docs\n"
            info += (
                "Note: Provides access to many different models through a unified API\n"
            )
        elif provider == "mock":
            info += "Description: Mock evaluator for testing/development\n"
            info += "No API key required\n"

        return info

    except ValueError as e:
        return f"Error: {e}"
