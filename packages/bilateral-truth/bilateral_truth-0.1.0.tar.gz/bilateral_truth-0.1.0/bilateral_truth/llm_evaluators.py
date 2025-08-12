"""
LLM-based evaluators for bilateral factuality assessment.

This module provides implementations that use language models to perform
bilateral evaluation of atomic formulas, assessing both verifiability
and refutability as described in the research paper.
"""

import os

# import json  # unused currently
from typing import Optional, Dict, List
from abc import ABC, abstractmethod
from collections import Counter
import random

from .assertions import Assertion
from .truth_values import GeneralizedTruthValue, TruthValueComponent


class LLMEvaluator(ABC):
    """Abstract base class for LLM-based evaluators."""

    @abstractmethod
    def evaluate_bilateral(
        self, assertion: Assertion, samples: int = 1
    ) -> GeneralizedTruthValue:
        """
        Perform bilateral evaluation of an assertion.

        Args:
            assertion: The assertion to evaluate
            samples: Number of samples to take for majority voting (default: 1)

        Returns:
            GeneralizedTruthValue with verifiability (u) and refutability (v) components
        """
        pass

    def evaluate_with_majority_voting(
        self, assertion: Assertion, samples: int, tiebreak_strategy: str = "random"
    ) -> GeneralizedTruthValue:
        """
        Evaluate assertion using multiple samples and majority voting.

        Args:
            assertion: The assertion to evaluate
            samples: Number of samples to take
            tiebreak_strategy: How to break ties ("random", "optimistic", "pessimistic")
                - "random": Randomly select from tied components
                - "optimistic": Prefer t (verified/refuted) - bias toward strong claims
                - "pessimistic": Prefer f (cannot verify/refute) - bias toward epistemic caution

        Returns:
            GeneralizedTruthValue determined by majority vote with tiebreaking
        """
        if samples <= 0:
            raise ValueError("Number of samples must be positive")

        if samples == 1:
            # Single sample - no voting needed
            return self._single_evaluation(assertion)

        # Collect multiple samples
        results = []
        for i in range(samples):
            try:
                result = self._single_evaluation(assertion)
                results.append(result)
            except Exception as e:
                print(f"Warning: Sample {i+1} failed: {e}")
                # Continue with fewer samples if some fail
                continue

        if not results:
            # All samples failed
            return GeneralizedTruthValue(TruthValueComponent.UNDEFINED, TruthValueComponent.UNDEFINED)

        # Apply majority voting
        return self._majority_vote(results, tiebreak_strategy)

    def _single_evaluation(self, assertion: Assertion) -> GeneralizedTruthValue:
        """
        Perform a single bilateral evaluation using separate verification and refutation calls.

        This implements Definition 3.4 from the paper with separate API calls.
        """
        try:
            # Make separate calls for verification and refutation
            u_component = self._evaluate_verification(assertion)
            v_component = self._evaluate_refutation(assertion)

            return GeneralizedTruthValue(u_component, v_component)

        except Exception as e:
            print(f"Warning: Bilateral evaluation failed: {e}")
            return GeneralizedTruthValue(TruthValueComponent.UNDEFINED, TruthValueComponent.UNDEFINED)

    def _majority_vote(
        self, results: List[GeneralizedTruthValue], tiebreak_strategy: str
    ) -> GeneralizedTruthValue:
        """
        Apply majority voting to a list of GeneralizedTruthValue results.

        Args:
            results: List of evaluation results
            tiebreak_strategy: Tiebreaking strategy

        Returns:
            The majority vote result with tiebreaking applied
        """
        if not results:
            return GeneralizedTruthValue(TruthValueComponent.UNDEFINED, TruthValueComponent.UNDEFINED)

        if len(results) == 1:
            return results[0]

        # Separate voting for verifiability (u) and refutability (v)
        u_votes = [result.u for result in results]
        v_votes = [result.v for result in results]

        # Get majority for each component
        u_majority = self._component_majority_vote(u_votes, tiebreak_strategy)
        v_majority = self._component_majority_vote(v_votes, tiebreak_strategy)

        return GeneralizedTruthValue(u_majority, v_majority)

    def _component_majority_vote(
        self, votes: List[TruthValueComponent], tiebreak_strategy: str
    ) -> TruthValueComponent:
        """
        Determine majority vote for a single component (u or v).

        Args:
            votes: List of TruthValueComponent votes
            tiebreak_strategy: How to break ties

        Returns:
            The winning TruthValueComponent
        """
        vote_counts = Counter(votes)

        # Find the maximum count
        max_count = max(vote_counts.values())
        winners = [
            component for component, count in vote_counts.items() if count == max_count
        ]

        if len(winners) == 1:
            # Clear winner
            return winners[0]

        # Tie detected - apply tiebreaking strategy
        return self._tiebreak(winners, tiebreak_strategy)

    def _tiebreak(
        self, tied_components: List[TruthValueComponent], strategy: str
    ) -> TruthValueComponent:
        """
        Break ties between components using the specified strategy.

        Args:
            tied_components: List of tied components
            strategy: Tiebreaking strategy ("random", "optimistic", "pessimistic")

        Returns:
            The component chosen by the tiebreaking strategy

        Tiebreaking Strategies:
        - "random": Randomly select from tied components
        - "optimistic": Prefer t (verified/refuted) > f (cannot verify/refute) > e (parse error)
        - "pessimistic": Prefer f (cannot verify/refute) > t (verified/refuted) > e (parse error)
        """
        if strategy == "random":
            return random.choice(tied_components)
        elif strategy == "optimistic":
            # Optimistic: prefer TRUE (verified/refuted) when in doubt
            if TruthValueComponent.TRUE in tied_components:
                return TruthValueComponent.TRUE
            elif TruthValueComponent.FALSE in tied_components:
                return TruthValueComponent.FALSE
            else:
                return TruthValueComponent.UNDEFINED
        elif strategy == "pessimistic":
            # Pessimistic: prefer FALSE (cannot verify/cannot refute) when in doubt
            if TruthValueComponent.FALSE in tied_components:
                return TruthValueComponent.FALSE
            elif TruthValueComponent.TRUE in tied_components:
                return TruthValueComponent.TRUE
            else:
                return TruthValueComponent.UNDEFINED
        else:
            # Default to random for unknown strategies
            return random.choice(tied_components)

    def _create_verification_prompt(self, assertion: Assertion) -> str:
        """
        Create a prompt for verification assessment as per Definition 3.4.

        The LLM must respond with exactly "VERIFIED" or "CANNOT VERIFY".
        """
        return f"""You are tasked with determining whether the following assertion can be verified as true based on available evidence and knowledge.

Assertion: {assertion}

Your task is to determine if this assertion can be verified. Consider all available evidence, facts, and reliable sources of information.

You must respond with exactly one of these two token sequences:
- VERIFIED (if the assertion can be confirmed as true based on evidence)
- CANNOT VERIFY (if the assertion cannot be confirmed as true, either due to lack of evidence, uncertainty, or because it is false)

Do not provide any explanation or additional text. Respond with only the required token sequence.

Response:"""

    def _create_refutation_prompt(self, assertion: Assertion) -> str:
        """
        Create a prompt for refutation assessment as per Definition 3.4.

        The LLM must respond with exactly "REFUTED" or "CANNOT REFUTE".
        """
        return f"""You are tasked with determining whether the following assertion can be refuted (shown to be false) based on available evidence and knowledge.

Assertion: {assertion}

Your task is to determine if this assertion can be refuted. Consider all available evidence, facts, and reliable sources of information that might contradict the assertion.

You must respond with exactly one of these two token sequences:
- REFUTED (if the assertion can be shown to be false based on evidence)
- CANNOT REFUTE (if the assertion cannot be shown to be false, either due to lack of contradictory evidence, uncertainty, or because it is true)

Do not provide any explanation or additional text. Respond with only the required token sequence.

Response:"""

    def _parse_verification_response(self, response_text: str) -> TruthValueComponent:
        """
        Parse verification response to extract verifiability value.

        Args:
            response_text: Raw response from the LLM

        Returns:
            TruthValueComponent for verifiability (u)
        """
        # Clean up the response
        response = response_text.strip().upper()

        # Look for exact token sequences as per Definition 3.4
        if "VERIFIED" in response and "CANNOT VERIFY" not in response:
            return TruthValueComponent.TRUE
        elif "CANNOT VERIFY" in response:
            return TruthValueComponent.FALSE
        else:
            # Model failed to return required token sequence - return empty
            return TruthValueComponent.UNDEFINED

    def _parse_refutation_response(self, response_text: str) -> TruthValueComponent:
        """
        Parse refutation response to extract refutability value.

        Args:
            response_text: Raw response from the LLM

        Returns:
            TruthValueComponent for refutability (v)
        """
        # Clean up the response
        response = response_text.strip().upper()

        # Look for exact token sequences as per Definition 3.4
        if "REFUTED" in response and "CANNOT REFUTE" not in response:
            return TruthValueComponent.TRUE
        elif "CANNOT REFUTE" in response:
            return TruthValueComponent.FALSE
        else:
            # Model failed to return required token sequence - return empty
            return TruthValueComponent.UNDEFINED

    def _evaluate_verification(self, assertion: Assertion) -> TruthValueComponent:
        """
        Evaluate verification component separately.
        Must be overridden by concrete evaluator classes.
        """
        raise NotImplementedError("Subclasses must implement _evaluate_verification")

    def _evaluate_refutation(self, assertion: Assertion) -> TruthValueComponent:
        """
        Evaluate refutation component separately.
        Must be overridden by concrete evaluator classes.
        """
        raise NotImplementedError("Subclasses must implement _evaluate_refutation")


class OpenAIEvaluator(LLMEvaluator):
    """LLM evaluator using OpenAI's API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize OpenAI evaluator.

        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY environment variable
            model: Model name to use (default: gpt-4)
        """
        try:
            import openai
        except ImportError:
            raise ImportError(
                "openai package is required. Install with: pip install openai"
            )

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key must be provided or set in OPENAI_API_KEY environment variable"
            )

        self.model = model
        self.client = openai.OpenAI(api_key=self.api_key)

    def evaluate_bilateral(
        self, assertion: Assertion, samples: int = 1
    ) -> GeneralizedTruthValue:
        """Evaluate assertion using OpenAI API with optional sampling."""
        if samples > 1:
            return self.evaluate_with_majority_voting(assertion, samples)
        return self._single_evaluation(assertion)

    def _evaluate_verification(self, assertion: Assertion) -> TruthValueComponent:
        """Evaluate verification using OpenAI API."""
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

            # Add temperature only for models that support it (GPT-5 series don't support temperature=0.0)
            if not self.model.startswith("gpt-5"):
                request_params["temperature"] = (
                    0.0  # Zero temperature for consistent token responses
                )

            response = self.client.chat.completions.create(**request_params)

            response_text = response.choices[0].message.content
            return self._parse_verification_response(response_text)

        except Exception as e:
            print(f"Warning: OpenAI verification call failed: {e}")
            return TruthValueComponent.UNDEFINED

    def _evaluate_refutation(self, assertion: Assertion) -> TruthValueComponent:
        """Evaluate refutation using OpenAI API."""
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

            # Add temperature only for models that support it (GPT-5 series don't support temperature=0.0)
            if not self.model.startswith("gpt-5"):
                request_params["temperature"] = (
                    0.0  # Zero temperature for consistent token responses
                )

            response = self.client.chat.completions.create(**request_params)

            response_text = response.choices[0].message.content
            return self._parse_refutation_response(response_text)

        except Exception as e:
            print(f"Warning: OpenAI refutation call failed: {e}")
            return TruthValueComponent.UNDEFINED


class AnthropicEvaluator(LLMEvaluator):
    """LLM evaluator using Anthropic's Claude API."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"
    ):
        """
        Initialize Anthropic evaluator.

        Args:
            api_key: Anthropic API key. If None, reads from ANTHROPIC_API_KEY environment variable
            model: Model name to use (default: claude-sonnet-4-20250514)
        """
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic package is required. Install with: pip install anthropic"
            )

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key must be provided or set in ANTHROPIC_API_KEY environment variable"
            )

        self.model = model
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def evaluate_bilateral(
        self, assertion: Assertion, samples: int = 1
    ) -> GeneralizedTruthValue:
        """Evaluate assertion using Anthropic API with optional sampling."""
        if samples > 1:
            return self.evaluate_with_majority_voting(assertion, samples)
        return self._single_evaluation(assertion)

    def _evaluate_verification(self, assertion: Assertion) -> TruthValueComponent:
        """Evaluate verification using Anthropic API."""
        try:
            prompt = self._create_verification_prompt(assertion)

            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,  # Only need a few tokens for response
                temperature=0.0,  # Zero temperature for consistent token responses
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = response.content[0].text
            return self._parse_verification_response(response_text)

        except Exception as e:
            print(f"Warning: Anthropic verification call failed: {e}")
            return TruthValueComponent.UNDEFINED

    def _evaluate_refutation(self, assertion: Assertion) -> TruthValueComponent:
        """Evaluate refutation using Anthropic API."""
        try:
            prompt = self._create_refutation_prompt(assertion)

            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,  # Only need a few tokens for response
                temperature=0.0,  # Zero temperature for consistent token responses
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = response.content[0].text
            return self._parse_refutation_response(response_text)

        except Exception as e:
            print(f"Warning: Anthropic refutation call failed: {e}")
            return TruthValueComponent.UNDEFINED


class MockLLMEvaluator(LLMEvaluator):
    """Mock LLM evaluator for testing and demonstration purposes."""

    def __init__(self, responses: Optional[Dict[str, GeneralizedTruthValue]] = None):
        """
        Initialize mock evaluator.

        Args:
            responses: Dictionary mapping assertion strings to predefined responses
        """
        self.responses = responses or {}

    def evaluate_bilateral(
        self, assertion: Assertion, samples: int = 1
    ) -> GeneralizedTruthValue:
        """Return predefined response or simulate evaluation with optional sampling."""
        if samples > 1:
            return self.evaluate_with_majority_voting(assertion, samples)
        return self._single_evaluation(assertion)

    def _evaluate_verification(self, assertion: Assertion) -> TruthValueComponent:
        """Mock verification evaluation using predefined logic."""
        assertion_str = str(assertion)

        # Return predefined response if available
        if assertion_str in self.responses:
            return self.responses[assertion_str].u

        # Simulate verification based on assertion content
        predicate = assertion.predicate.lower()

        # Check for weather-related content
        weather_keywords = [
            "sunny",
            "clear",
            "bright",
            "raining",
            "cloudy",
            "stormy",
            "rain",
            "cloud",
            "storm",
        ]
        if any(keyword in predicate for keyword in weather_keywords):
            # Weather statements - generally verifiable
            return TruthValueComponent.TRUE
        elif (
            predicate.startswith("love")
            or predicate.startswith("like")
            or "love" in predicate
            or "like" in predicate
        ):
            # Emotional statements - hard to verify
            return TruthValueComponent.UNDEFINED
        elif any(keyword in predicate for keyword in ["true", "correct", "valid"]):
            # Meta-truth statements
            return TruthValueComponent.TRUE
        elif any(keyword in predicate for keyword in ["false", "incorrect", "invalid"]):
            # Meta-false statements
            return TruthValueComponent.FALSE
        else:
            # Unknown predicates
            return TruthValueComponent.UNDEFINED

    def _evaluate_refutation(self, assertion: Assertion) -> TruthValueComponent:
        """Mock refutation evaluation using predefined logic."""
        assertion_str = str(assertion)

        # Return predefined response if available
        if assertion_str in self.responses:
            return self.responses[assertion_str].v

        # Simulate refutation based on assertion content
        predicate = assertion.predicate.lower()

        # Check for different types of weather content
        if any(keyword in predicate for keyword in ["sunny", "clear", "bright"]):
            # Positive weather statements - not always refutable
            return TruthValueComponent.UNDEFINED
        elif any(
            keyword in predicate
            for keyword in ["raining", "cloudy", "stormy", "rain", "cloud", "storm"]
        ):
            # Variable weather statements - refutable
            return TruthValueComponent.TRUE
        elif (
            predicate.startswith("love")
            or predicate.startswith("like")
            or "love" in predicate
            or "like" in predicate
        ):
            # Emotional statements - hard to refute
            return TruthValueComponent.UNDEFINED
        elif any(keyword in predicate for keyword in ["true", "correct", "valid"]):
            # Meta-truth statements
            return TruthValueComponent.FALSE
        elif any(keyword in predicate for keyword in ["false", "incorrect", "invalid"]):
            # Meta-false statements
            return TruthValueComponent.TRUE
        else:
            # Unknown predicates
            return TruthValueComponent.UNDEFINED


def create_llm_evaluator(provider: str = "mock", **kwargs) -> LLMEvaluator:
    """
    Factory function to create LLM evaluators.

    Args:
        provider: LLM provider ('openai', 'anthropic', 'mock')
        **kwargs: Additional arguments passed to the evaluator constructor

    Returns:
        LLMEvaluator instance
    """
    if provider.lower() == "openai":
        return OpenAIEvaluator(**kwargs)
    elif provider.lower() == "anthropic":
        return AnthropicEvaluator(**kwargs)
    elif provider.lower() == "mock":
        return MockLLMEvaluator(**kwargs)
    else:
        raise ValueError(
            f"Unknown provider: {provider}. Supported: 'openai', 'anthropic', 'mock'"
        )
