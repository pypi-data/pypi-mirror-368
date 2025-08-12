"""
Integration tests for LLM evaluators with real API calls.

These tests require actual API keys and make real API calls.
They are designed to verify that the separate verification/refutation approach
works correctly with actual LLM providers.

To run these tests:
1. Set up API keys in environment variables or .env file:
   - OPENAI_API_KEY
   - ANTHROPIC_API_KEY
   - OPENROUTER_API_KEY
2. Run with: pytest tests/test_integration.py -v -s

Note: These tests may incur API costs and are slower than unit tests.
They can be skipped by running: pytest tests/ -k "not integration"
"""

import unittest
import os
import pytest

# from unittest.mock import patch  # unused currently

from bilateral_truth import Assertion, GeneralizedTruthValue, TruthValueComponent
from bilateral_truth.llm_evaluators import OpenAIEvaluator, AnthropicEvaluator
from bilateral_truth.model_router import OpenRouterEvaluator


class IntegrationTestBase(unittest.TestCase):
    """Base class for integration tests with common utilities."""

    def setUp(self):
        """Set up test environment."""
        # Load .env file if it exists
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            pass

    def check_api_key(self, provider: str) -> bool:
        """Check if API key is available for a provider."""
        key_mapping = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
        }
        return bool(os.getenv(key_mapping.get(provider)))

    def skip_if_no_key(self, provider: str):
        """Skip test if API key is not available."""
        if not self.check_api_key(provider):
            pytest.skip(
                f"No API key found for {provider}. Set {provider.upper()}_API_KEY environment variable."
            )

    def assert_valid_truth_value(self, result: GeneralizedTruthValue):
        """Assert that result is a valid GeneralizedTruthValue."""
        self.assertIsInstance(result, GeneralizedTruthValue)
        self.assertIn(
            result.u,
            [
                TruthValueComponent.TRUE,
                TruthValueComponent.FALSE,
                TruthValueComponent.UNDEFINED,
            ],
        )
        self.assertIn(
            result.v,
            [
                TruthValueComponent.TRUE,
                TruthValueComponent.FALSE,
                TruthValueComponent.UNDEFINED,
            ],
        )

    def assert_token_sequence_compliance(self, evaluator, assertion: Assertion):
        """Test that separate evaluation methods return valid components."""
        u_component = evaluator._evaluate_verification(assertion)
        v_component = evaluator._evaluate_refutation(assertion)

        self.assertIn(
            u_component,
            [
                TruthValueComponent.TRUE,
                TruthValueComponent.FALSE,
                TruthValueComponent.UNDEFINED,
            ],
        )
        self.assertIn(
            v_component,
            [
                TruthValueComponent.TRUE,
                TruthValueComponent.FALSE,
                TruthValueComponent.UNDEFINED,
            ],
        )

        # Test that full evaluation matches separate components
        full_result = evaluator.evaluate_bilateral(assertion)
        self.assertEqual(full_result.u, u_component)
        self.assertEqual(full_result.v, v_component)


@pytest.mark.integration
class TestOpenAIIntegration(IntegrationTestBase):
    """Integration tests for OpenAI evaluator."""

    def setUp(self):
        super().setUp()
        self.skip_if_no_key("openai")

    def test_openai_gpt4_factual_statement(self):
        """Test OpenAI GPT-4 with a clear factual statement."""
        evaluator = OpenAIEvaluator(model="gpt-4")
        assertion = Assertion("The capital of France is Paris")

        result = evaluator.evaluate_bilateral(assertion)

        self.assert_valid_truth_value(result)
        # For a clear factual statement, we expect it to be verifiable
        # (though we don't enforce specific results in integration tests)
        print(f"OpenAI GPT-4: '{assertion}' -> {result}")

    def test_openai_gpt4_false_statement(self):
        """Test OpenAI GPT-4 with a clearly false statement."""
        evaluator = OpenAIEvaluator(model="gpt-4")
        assertion = Assertion("The Earth is flat")

        result = evaluator.evaluate_bilateral(assertion)

        self.assert_valid_truth_value(result)
        print(f"OpenAI GPT-4: '{assertion}' -> {result}")

    def test_openai_gpt4_uncertain_statement(self):
        """Test OpenAI GPT-4 with an uncertain statement."""
        evaluator = OpenAIEvaluator(model="gpt-4")
        assertion = Assertion("There will be rain tomorrow")

        result = evaluator.evaluate_bilateral(assertion)

        self.assert_valid_truth_value(result)
        print(f"OpenAI GPT-4: '{assertion}' -> {result}")

    def test_openai_separate_evaluation_consistency(self):
        """Test that separate evaluation methods are consistent with full evaluation."""
        evaluator = OpenAIEvaluator(model="gpt-4")
        assertion = Assertion("Water boils at 100 degrees Celsius at sea level")

        self.assert_token_sequence_compliance(evaluator, assertion)
        print(f"OpenAI GPT-4 separate evaluation test passed for: '{assertion}'")

    def test_openai_token_sequence_parsing(self):
        """Test that OpenAI returns valid token sequences that we can parse."""
        evaluator = OpenAIEvaluator(model="gpt-4")
        assertion = Assertion("2 + 2 = 4")

        # Test verification call directly
        u_component = evaluator._evaluate_verification(assertion)
        self.assertIn(
            u_component,
            [
                TruthValueComponent.TRUE,
                TruthValueComponent.FALSE,
                TruthValueComponent.UNDEFINED,
            ],
        )

        # Test refutation call directly
        v_component = evaluator._evaluate_refutation(assertion)
        self.assertIn(
            v_component,
            [
                TruthValueComponent.TRUE,
                TruthValueComponent.FALSE,
                TruthValueComponent.UNDEFINED,
            ],
        )

        print(
            f"OpenAI GPT-4 token sequences: verification={u_component.value}, refutation={v_component.value}"
        )

    def test_openai_gpt4_mini_comparison(self):
        """Test OpenAI GPT-4 Turbo to compare with GPT-5."""
        evaluator = OpenAIEvaluator(model="gpt-4-turbo")
        assertion = Assertion("The speed of light is approximately 300,000 km/s")

        result = evaluator.evaluate_bilateral(assertion)

        self.assert_valid_truth_value(result)
        print(f"OpenAI GPT-4 Turbo: '{assertion}' -> {result}")


@pytest.mark.integration
class TestAnthropicIntegration(IntegrationTestBase):
    """Integration tests for Anthropic evaluator."""

    def setUp(self):
        super().setUp()
        self.skip_if_no_key("anthropic")

    def test_anthropic_claude_factual_statement(self):
        """Test Anthropic Claude with a clear factual statement."""
        evaluator = AnthropicEvaluator(model="claude-sonnet-4-20250514")
        assertion = Assertion("Oxygen is necessary for human breathing")

        result = evaluator.evaluate_bilateral(assertion)

        self.assert_valid_truth_value(result)
        print(f"Anthropic Claude: '{assertion}' -> {result}")

    def test_anthropic_claude_false_statement(self):
        """Test Anthropic Claude with a clearly false statement."""
        evaluator = AnthropicEvaluator(model="claude-sonnet-4-20250514")
        assertion = Assertion("Humans can breathe underwater without equipment")

        result = evaluator.evaluate_bilateral(assertion)

        self.assert_valid_truth_value(result)
        print(f"Anthropic Claude: '{assertion}' -> {result}")

    def test_anthropic_claude_uncertain_statement(self):
        """Test Anthropic Claude with an uncertain statement."""
        evaluator = AnthropicEvaluator(model="claude-sonnet-4-20250514")
        assertion = Assertion("Artificial intelligence will solve climate change")

        result = evaluator.evaluate_bilateral(assertion)

        self.assert_valid_truth_value(result)
        print(f"Anthropic Claude: '{assertion}' -> {result}")

    def test_anthropic_separate_evaluation_consistency(self):
        """Test that separate evaluation methods are consistent with full evaluation."""
        evaluator = AnthropicEvaluator(model="claude-sonnet-4-20250514")
        assertion = Assertion("The Great Wall of China is visible from space")

        self.assert_token_sequence_compliance(evaluator, assertion)
        print(f"Anthropic Claude separate evaluation test passed for: '{assertion}'")

    def test_anthropic_token_sequence_parsing(self):
        """Test that Anthropic returns valid token sequences that we can parse."""
        evaluator = AnthropicEvaluator(model="claude-sonnet-4-20250514")
        assertion = Assertion("Shakespeare wrote Romeo and Juliet")

        # Test verification call directly
        u_component = evaluator._evaluate_verification(assertion)
        self.assertIn(
            u_component,
            [
                TruthValueComponent.TRUE,
                TruthValueComponent.FALSE,
                TruthValueComponent.UNDEFINED,
            ],
        )

        # Test refutation call directly
        v_component = evaluator._evaluate_refutation(assertion)
        self.assertIn(
            v_component,
            [
                TruthValueComponent.TRUE,
                TruthValueComponent.FALSE,
                TruthValueComponent.UNDEFINED,
            ],
        )

        print(
            f"Anthropic Claude token sequences: verification={u_component.value}, refutation={v_component.value}"
        )

    def test_anthropic_claude_opus_comparison(self):
        """Test Anthropic Claude Opus 4 model."""
        evaluator = AnthropicEvaluator(model="claude-opus-4-20250514")
        assertion = Assertion("Mount Everest is the tallest mountain on Earth")

        result = evaluator.evaluate_bilateral(assertion)

        self.assert_valid_truth_value(result)
        print(f"Anthropic Claude Opus 4: '{assertion}' -> {result}")


@pytest.mark.integration
class TestOpenRouterIntegration(IntegrationTestBase):
    """Integration tests for OpenRouter evaluator."""

    def setUp(self):
        super().setUp()
        self.skip_if_no_key("openrouter")

    def test_openrouter_llama_factual_statement(self):
        """Test OpenRouter with Llama model."""
        evaluator = OpenRouterEvaluator(model="meta-llama/llama-3.1-8b-instruct")
        assertion = Assertion("The Pacific Ocean is the largest ocean on Earth")

        result = evaluator.evaluate_bilateral(assertion)

        self.assert_valid_truth_value(result)
        print(f"OpenRouter Llama: '{assertion}' -> {result}")

    def test_openrouter_mistral_false_statement(self):
        """Test OpenRouter with Mistral model."""
        evaluator = OpenRouterEvaluator(model="mistralai/mistral-7b-instruct")
        assertion = Assertion("The Sun revolves around the Earth")

        result = evaluator.evaluate_bilateral(assertion)

        self.assert_valid_truth_value(result)
        print(f"OpenRouter Mistral: '{assertion}' -> {result}")

    def test_openrouter_separate_evaluation_consistency(self):
        """Test that OpenRouter separate evaluation methods are consistent."""
        evaluator = OpenRouterEvaluator(model="meta-llama/llama-3.1-8b-instruct")
        assertion = Assertion("Photosynthesis converts sunlight into chemical energy")

        self.assert_token_sequence_compliance(evaluator, assertion)
        print(f"OpenRouter separate evaluation test passed for: '{assertion}'")

    def test_openrouter_token_sequence_parsing(self):
        """Test that OpenRouter returns valid token sequences."""
        evaluator = OpenRouterEvaluator(model="mistralai/mistral-7b-instruct")
        assertion = Assertion("DNA stands for deoxyribonucleic acid")

        # Test verification call directly
        u_component = evaluator._evaluate_verification(assertion)
        self.assertIn(
            u_component,
            [
                TruthValueComponent.TRUE,
                TruthValueComponent.FALSE,
                TruthValueComponent.UNDEFINED,
            ],
        )

        # Test refutation call directly
        v_component = evaluator._evaluate_refutation(assertion)
        self.assertIn(
            v_component,
            [
                TruthValueComponent.TRUE,
                TruthValueComponent.FALSE,
                TruthValueComponent.UNDEFINED,
            ],
        )

        print(
            f"OpenRouter token sequences: verification={u_component.value}, refutation={v_component.value}"
        )


@pytest.mark.integration
class TestCrossProviderComparison(IntegrationTestBase):
    """Integration tests comparing results across different providers."""

    def setUp(self):
        super().setUp()

        # Determine which providers are available
        self.available_providers = []
        if self.check_api_key("openai"):
            self.available_providers.append(
                ("OpenAI GPT-4", lambda: OpenAIEvaluator(model="gpt-4"))
            )
        if self.check_api_key("anthropic"):
            self.available_providers.append(
                (
                    "Anthropic Claude Sonnet 4",
                    lambda: AnthropicEvaluator(model="claude-sonnet-4-20250514"),
                )
            )
        if self.check_api_key("openrouter"):
            self.available_providers.append(
                (
                    "OpenRouter Llama",
                    lambda: OpenRouterEvaluator(
                        model="meta-llama/llama-3.1-8b-instruct"
                    ),
                )
            )

        if len(self.available_providers) < 2:
            pytest.skip(
                "Need at least 2 providers with API keys for cross-provider comparison"
            )

    def test_obvious_truth_cross_provider(self):
        """Test an obvious truth across multiple providers."""
        assertion = Assertion("Water freezes at 0 degrees Celsius")
        results = {}

        for provider_name, evaluator_factory in self.available_providers:
            evaluator = evaluator_factory()
            result = evaluator.evaluate_bilateral(assertion)
            results[provider_name] = result
            print(f"{provider_name}: '{assertion}' -> {result}")

        # All results should be valid
        for provider, result in results.items():
            self.assert_valid_truth_value(result)

    def test_obvious_falsehood_cross_provider(self):
        """Test an obvious falsehood across multiple providers."""
        assertion = Assertion("1 + 1 = 3")
        results = {}

        for provider_name, evaluator_factory in self.available_providers:
            evaluator = evaluator_factory()
            result = evaluator.evaluate_bilateral(assertion)
            results[provider_name] = result
            print(f"{provider_name}: '{assertion}' -> {result}")

        # All results should be valid
        for provider, result in results.items():
            self.assert_valid_truth_value(result)

    def test_uncertain_statement_cross_provider(self):
        """Test an uncertain statement across multiple providers."""
        assertion = Assertion("It will rain next Tuesday")
        results = {}

        for provider_name, evaluator_factory in self.available_providers:
            evaluator = evaluator_factory()
            result = evaluator.evaluate_bilateral(assertion)
            results[provider_name] = result
            print(f"{provider_name}: '{assertion}' -> {result}")

        # All results should be valid
        for provider, result in results.items():
            self.assert_valid_truth_value(result)

    def test_definition_34_compliance_cross_provider(self):
        """Test that all providers properly implement Definition 3.4 token sequences."""
        assertion = Assertion("The chemical symbol for gold is Au")

        for provider_name, evaluator_factory in self.available_providers:
            evaluator = evaluator_factory()

            # Test that separate methods work
            u_component = evaluator._evaluate_verification(assertion)
            v_component = evaluator._evaluate_refutation(assertion)

            # Test that components are valid
            self.assertIn(
                u_component,
                [
                    TruthValueComponent.TRUE,
                    TruthValueComponent.FALSE,
                    TruthValueComponent.UNDEFINED,
                ],
            )
            self.assertIn(
                v_component,
                [
                    TruthValueComponent.TRUE,
                    TruthValueComponent.FALSE,
                    TruthValueComponent.UNDEFINED,
                ],
            )

            # Test that full evaluation matches
            full_result = evaluator.evaluate_bilateral(assertion)
            self.assertEqual(full_result.u, u_component)
            self.assertEqual(full_result.v, v_component)

            print(f"{provider_name} Definition 3.4 compliance: ✓")


@pytest.mark.integration
class TestSamplingIntegration(IntegrationTestBase):
    """Integration tests for sampling and majority voting with real APIs."""

    def setUp(self):
        super().setUp()
        # Use the first available provider
        if self.check_api_key("openai"):
            self.evaluator = OpenAIEvaluator(
                model="gpt-4-turbo"
            )  # Use cheaper model for sampling
            self.provider_name = "OpenAI GPT-4 Turbo"
        elif self.check_api_key("anthropic"):
            self.evaluator = AnthropicEvaluator(
                model="claude-sonnet-4-20250514"
            )  # Use Sonnet 4
            self.provider_name = "Anthropic Claude Sonnet 4"
        elif self.check_api_key("openrouter"):
            self.evaluator = OpenRouterEvaluator(model="mistralai/mistral-7b-instruct")
            self.provider_name = "OpenRouter Mistral"
        else:
            pytest.skip("No API key available for sampling tests")

    def test_sampling_with_majority_voting(self):
        """Test sampling with majority voting using real API calls."""
        assertion = Assertion("Gravity causes objects to fall towards Earth")
        samples = 3  # Keep small to avoid excessive API costs

        result = self.evaluator.evaluate_with_majority_voting(
            assertion, samples, "random"
        )

        self.assert_valid_truth_value(result)
        print(f"{self.provider_name} with {samples} samples: '{assertion}' -> {result}")

    def test_sampling_consistency(self):
        """Test that sampling returns consistent types of results."""
        assertion = Assertion("The atomic number of hydrogen is 1")

        # Test with different sample sizes
        for samples in [1, 3]:
            result = self.evaluator.evaluate_with_majority_voting(
                assertion, samples, "pessimistic"
            )
            self.assert_valid_truth_value(result)
            print(f"{self.provider_name} {samples} samples: {result}")

    def test_tiebreaking_strategies(self):
        """Test different tiebreaking strategies with even number of samples."""
        assertion = Assertion("Quantum physics is counterintuitive")
        samples = 2  # Even number to potentially cause ties

        for strategy in ["random", "pessimistic", "optimistic"]:
            result = self.evaluator.evaluate_with_majority_voting(
                assertion, samples, strategy
            )
            self.assert_valid_truth_value(result)
            print(f"{self.provider_name} tiebreak {strategy}: {result}")


if __name__ == "__main__":
    # Run with verbose output and don't capture stdout/stderr so we can see the results
    pytest.main([__file__, "-v", "-s"])
