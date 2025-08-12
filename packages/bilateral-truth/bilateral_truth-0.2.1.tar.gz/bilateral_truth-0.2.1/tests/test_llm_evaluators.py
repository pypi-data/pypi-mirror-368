"""Tests for LLM evaluator implementations."""

import unittest
from unittest.mock import patch, MagicMock
from bilateral_truth.assertions import Assertion
from bilateral_truth.truth_values import GeneralizedTruthValue, TruthValueComponent
from bilateral_truth.llm_evaluators import (
    MockLLMEvaluator,
    create_llm_evaluator,
    OpenAIEvaluator,
    AnthropicEvaluator,
)


class TestMockLLMEvaluator(unittest.TestCase):
    """Test the MockLLMEvaluator class."""

    def test_predefined_responses(self):
        """Test evaluator with predefined responses."""
        responses = {
            "The sky is blue": GeneralizedTruthValue(
                TruthValueComponent.TRUE, TruthValueComponent.FALSE
            ),
            "It is raining": GeneralizedTruthValue(
                TruthValueComponent.FALSE, TruthValueComponent.TRUE
            ),
        }

        evaluator = MockLLMEvaluator(responses)

        assertion1 = Assertion("The sky is blue")
        assertion2 = Assertion("It is raining")
        assertion3 = Assertion("Unknown statement")

        result1 = evaluator.evaluate_bilateral(assertion1)
        result2 = evaluator.evaluate_bilateral(assertion2)
        result3 = evaluator.evaluate_bilateral(assertion3)

        self.assertEqual(
            result1,
            GeneralizedTruthValue(TruthValueComponent.TRUE, TruthValueComponent.FALSE),
        )
        self.assertEqual(
            result2,
            GeneralizedTruthValue(TruthValueComponent.FALSE, TruthValueComponent.TRUE),
        )
        # Unknown statement should use mock logic
        self.assertIsInstance(result3, GeneralizedTruthValue)

    def test_weather_simulation(self):
        """Test mock evaluation logic for weather statements."""
        evaluator = MockLLMEvaluator()

        # Test exact predicate matches
        sunny_assertion = Assertion("sunny")
        raining_assertion = Assertion("raining")

        # Test natural language statements with weather keywords
        sunny_natural = Assertion("It is sunny today")
        cloudy_natural = Assertion("The sky is cloudy")

        sunny_result = evaluator.evaluate_bilateral(sunny_assertion)
        raining_result = evaluator.evaluate_bilateral(raining_assertion)
        sunny_nat_result = evaluator.evaluate_bilateral(sunny_natural)
        cloudy_nat_result = evaluator.evaluate_bilateral(cloudy_natural)

        # All weather statements should be verifiable
        self.assertEqual(sunny_result.u, TruthValueComponent.TRUE)
        self.assertEqual(raining_result.u, TruthValueComponent.TRUE)
        self.assertEqual(sunny_nat_result.u, TruthValueComponent.TRUE)
        self.assertEqual(cloudy_nat_result.u, TruthValueComponent.TRUE)

        # Sunny weather is not refutable, variable weather is refutable
        self.assertEqual(sunny_result.v, TruthValueComponent.UNDEFINED)
        self.assertEqual(raining_result.v, TruthValueComponent.TRUE)
        self.assertEqual(sunny_nat_result.v, TruthValueComponent.UNDEFINED)
        self.assertEqual(cloudy_nat_result.v, TruthValueComponent.TRUE)

    def test_emotional_statements(self):
        """Test mock evaluation logic for emotional statements."""
        evaluator = MockLLMEvaluator()

        love_assertion = Assertion("loves", "alice", "bob")
        like_assertion = Assertion("likes", "john", "mary")
        love_natural = Assertion("I love pizza")
        like_natural = Assertion("She likes music")

        love_result = evaluator.evaluate_bilateral(love_assertion)
        like_result = evaluator.evaluate_bilateral(like_assertion)
        love_nat_result = evaluator.evaluate_bilateral(love_natural)
        like_nat_result = evaluator.evaluate_bilateral(like_natural)

        # Emotional statements should be hard to verify or refute
        self.assertEqual(
            love_result,
            GeneralizedTruthValue(
                TruthValueComponent.UNDEFINED, TruthValueComponent.UNDEFINED
            ),
        )
        self.assertEqual(
            like_result,
            GeneralizedTruthValue(
                TruthValueComponent.UNDEFINED, TruthValueComponent.UNDEFINED
            ),
        )
        self.assertEqual(
            love_nat_result,
            GeneralizedTruthValue(
                TruthValueComponent.UNDEFINED, TruthValueComponent.UNDEFINED
            ),
        )
        self.assertEqual(
            like_nat_result,
            GeneralizedTruthValue(
                TruthValueComponent.UNDEFINED, TruthValueComponent.UNDEFINED
            ),
        )

    def test_meta_truth_statements(self):
        """Test mock evaluation logic for meta-truth statements."""
        evaluator = MockLLMEvaluator()

        true_assertion = Assertion("true")
        false_assertion = Assertion("false")
        valid_assertion = Assertion("valid")
        statement_with_true = Assertion("This statement is true")

        true_result = evaluator.evaluate_bilateral(true_assertion)
        false_result = evaluator.evaluate_bilateral(false_assertion)
        valid_result = evaluator.evaluate_bilateral(valid_assertion)
        statement_result = evaluator.evaluate_bilateral(statement_with_true)

        self.assertEqual(
            true_result,
            GeneralizedTruthValue(TruthValueComponent.TRUE, TruthValueComponent.FALSE),
        )
        self.assertEqual(
            false_result,
            GeneralizedTruthValue(TruthValueComponent.FALSE, TruthValueComponent.TRUE),
        )
        self.assertEqual(
            valid_result,
            GeneralizedTruthValue(TruthValueComponent.TRUE, TruthValueComponent.FALSE),
        )
        self.assertEqual(
            statement_result,
            GeneralizedTruthValue(TruthValueComponent.TRUE, TruthValueComponent.FALSE),
        )


class TestEvaluatorFactory(unittest.TestCase):
    """Test the create_llm_evaluator factory function."""

    def test_create_mock_evaluator(self):
        """Test creating mock evaluator."""
        evaluator = create_llm_evaluator("mock")
        self.assertIsInstance(evaluator, MockLLMEvaluator)
        # Test that it has the new separate evaluation methods
        self.assertTrue(hasattr(evaluator, "_evaluate_verification"))
        self.assertTrue(hasattr(evaluator, "_evaluate_refutation"))

    def test_create_mock_with_responses(self):
        """Test creating mock evaluator with predefined responses."""
        responses = {
            "test": GeneralizedTruthValue(
                TruthValueComponent.TRUE, TruthValueComponent.FALSE
            )
        }
        evaluator = create_llm_evaluator("mock", responses=responses)
        self.assertIsInstance(evaluator, MockLLMEvaluator)

        assertion = Assertion("test")
        result = evaluator.evaluate_bilateral(assertion)
        self.assertEqual(
            result,
            GeneralizedTruthValue(TruthValueComponent.TRUE, TruthValueComponent.FALSE),
        )

        # Test that separate evaluation methods work with predefined responses
        u_result = evaluator._evaluate_verification(assertion)
        v_result = evaluator._evaluate_refutation(assertion)
        self.assertEqual(u_result, TruthValueComponent.TRUE)
        self.assertEqual(v_result, TruthValueComponent.FALSE)

    def test_invalid_provider(self):
        """Test creating evaluator with invalid provider."""
        with self.assertRaises(ValueError):
            create_llm_evaluator("invalid_provider")


class TestOpenAIEvaluator(unittest.TestCase):
    """Test the OpenAIEvaluator class."""

    def test_missing_api_key(self):
        """Test that missing API key raises ValueError when openai package is available."""
        try:
            import openai
            # Only test API key validation if package is installed
            with patch.dict("os.environ", {}, clear=True):
                with self.assertRaises(ValueError):
                    OpenAIEvaluator()
        except ImportError:
            # Skip test if openai package not available
            self.skipTest("openai package not available")

    def test_missing_openai_package(self):
        """Test that missing openai package raises ImportError."""
        with patch.dict("sys.modules", {"openai": None}):
            with self.assertRaises(ImportError):
                OpenAIEvaluator(api_key="test")

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    @patch("builtins.__import__")
    def test_token_parsing_with_mocked_import(self, mock_import):
        """Test token parsing methods with mocked openai import."""

        # Mock the openai import to avoid actual dependency
        def mock_import_func(name, *args, **kwargs):
            if name == "openai":
                mock_openai = MagicMock()
                mock_openai.OpenAI = MagicMock()
                return mock_openai
            else:
                # Use real import for other modules
                return __import__(name, *args, **kwargs)

        mock_import.side_effect = mock_import_func

        evaluator = OpenAIEvaluator()

        # Test token parsing methods directly
        self.assertEqual(
            evaluator._parse_verification_response("VERIFIED"), TruthValueComponent.TRUE
        )
        self.assertEqual(
            evaluator._parse_verification_response("CANNOT VERIFY"),
            TruthValueComponent.FALSE,
        )
        self.assertEqual(
            evaluator._parse_refutation_response("REFUTED"), TruthValueComponent.TRUE
        )
        self.assertEqual(
            evaluator._parse_refutation_response("CANNOT REFUTE"),
            TruthValueComponent.FALSE,
        )

    def test_token_sequence_parsing_methods_exist(self):
        """Test that OpenAI evaluator has the token parsing methods."""
        # We can test the class structure without actually creating an instance
        self.assertTrue(hasattr(OpenAIEvaluator, "_parse_verification_response"))
        self.assertTrue(hasattr(OpenAIEvaluator, "_parse_refutation_response"))
        self.assertTrue(hasattr(OpenAIEvaluator, "_evaluate_verification"))
        self.assertTrue(hasattr(OpenAIEvaluator, "_evaluate_refutation"))

    def test_openai_evaluator_inheritance(self):
        """Test that OpenAI evaluator inherits from LLMEvaluator properly."""
        from bilateral_truth.llm_evaluators import LLMEvaluator

        self.assertTrue(issubclass(OpenAIEvaluator, LLMEvaluator))

        # Test that it implements the required abstract methods
        required_methods = ["_evaluate_verification", "_evaluate_refutation"]
        for method in required_methods:
            self.assertTrue(hasattr(OpenAIEvaluator, method))


class TestAnthropicEvaluator(unittest.TestCase):
    """Test the AnthropicEvaluator class."""

    def test_missing_api_key(self):
        """Test that missing API key raises ValueError when anthropic package is available."""
        try:
            import anthropic
            # Only test API key validation if package is installed
            with patch.dict("os.environ", {}, clear=True):
                with self.assertRaises(ValueError):
                    AnthropicEvaluator()
        except ImportError:
            # Skip test if anthropic package not available
            self.skipTest("anthropic package not available")

    def test_missing_anthropic_package(self):
        """Test that missing anthropic package raises ImportError."""
        with patch.dict("sys.modules", {"anthropic": None}):
            with self.assertRaises(ImportError):
                AnthropicEvaluator(api_key="test")

    def test_anthropic_evaluator_inheritance(self):
        """Test that Anthropic evaluator inherits from LLMEvaluator properly."""
        from bilateral_truth.llm_evaluators import LLMEvaluator

        self.assertTrue(issubclass(AnthropicEvaluator, LLMEvaluator))

        # Test that it implements the required abstract methods
        required_methods = ["_evaluate_verification", "_evaluate_refutation"]
        for method in required_methods:
            self.assertTrue(hasattr(AnthropicEvaluator, method))

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    @patch("builtins.__import__")
    def test_token_parsing_with_mocked_import(self, mock_import):
        """Test token parsing methods with mocked anthropic import."""

        # Mock the anthropic import to avoid actual dependency
        def mock_import_func(name, *args, **kwargs):
            if name == "anthropic":
                mock_anthropic = MagicMock()
                mock_anthropic.Anthropic = MagicMock()
                return mock_anthropic
            else:
                # Use real import for other modules
                return __import__(name, *args, **kwargs)

        mock_import.side_effect = mock_import_func

        evaluator = AnthropicEvaluator()

        # Test token parsing methods directly - these are inherited from base class
        self.assertEqual(
            evaluator._parse_verification_response("VERIFIED"), TruthValueComponent.TRUE
        )
        self.assertEqual(
            evaluator._parse_verification_response("CANNOT VERIFY"),
            TruthValueComponent.FALSE,
        )
        self.assertEqual(
            evaluator._parse_refutation_response("REFUTED"), TruthValueComponent.TRUE
        )
        self.assertEqual(
            evaluator._parse_refutation_response("CANNOT REFUTE"),
            TruthValueComponent.FALSE,
        )

    def test_token_sequence_parsing_methods_exist(self):
        """Test that Anthropic evaluator has the token parsing methods."""
        # We can test the class structure without actually creating an instance
        self.assertTrue(hasattr(AnthropicEvaluator, "_parse_verification_response"))
        self.assertTrue(hasattr(AnthropicEvaluator, "_parse_refutation_response"))
        self.assertTrue(hasattr(AnthropicEvaluator, "_evaluate_verification"))
        self.assertTrue(hasattr(AnthropicEvaluator, "_evaluate_refutation"))


class TestTokenSequenceParsing(unittest.TestCase):
    """Test token sequence parsing functionality."""

    def test_verification_token_parsing(self):
        """Test parsing verification token sequences."""
        evaluator = MockLLMEvaluator()

        # Test valid responses
        self.assertEqual(
            evaluator._parse_verification_response("VERIFIED"), TruthValueComponent.TRUE
        )
        self.assertEqual(
            evaluator._parse_verification_response("CANNOT VERIFY"),
            TruthValueComponent.FALSE,
        )

        # Test case insensitive
        self.assertEqual(
            evaluator._parse_verification_response("verified"), TruthValueComponent.TRUE
        )
        self.assertEqual(
            evaluator._parse_verification_response("cannot verify"),
            TruthValueComponent.FALSE,
        )

        # Test with extra text
        self.assertEqual(
            evaluator._parse_verification_response(
                "I believe this is VERIFIED based on evidence"
            ),
            TruthValueComponent.TRUE,
        )

        # Test invalid responses return EMPTY
        self.assertEqual(
            evaluator._parse_verification_response("Maybe true"),
            TruthValueComponent.UNDEFINED,
        )
        self.assertEqual(
            evaluator._parse_verification_response(""), TruthValueComponent.UNDEFINED
        )

    def test_refutation_token_parsing(self):
        """Test parsing refutation token sequences."""
        evaluator = MockLLMEvaluator()

        # Test valid responses
        self.assertEqual(
            evaluator._parse_refutation_response("REFUTED"), TruthValueComponent.TRUE
        )
        self.assertEqual(
            evaluator._parse_refutation_response("CANNOT REFUTE"),
            TruthValueComponent.FALSE,
        )

        # Test case insensitive
        self.assertEqual(
            evaluator._parse_refutation_response("refuted"), TruthValueComponent.TRUE
        )
        self.assertEqual(
            evaluator._parse_refutation_response("cannot refute"),
            TruthValueComponent.FALSE,
        )

        # Test with extra text
        self.assertEqual(
            evaluator._parse_refutation_response(
                "This statement is clearly REFUTED by the evidence"
            ),
            TruthValueComponent.TRUE,
        )

        # Test invalid responses return EMPTY
        self.assertEqual(
            evaluator._parse_refutation_response("Maybe false"),
            TruthValueComponent.UNDEFINED,
        )
        self.assertEqual(
            evaluator._parse_refutation_response(""), TruthValueComponent.UNDEFINED
        )

    def test_separate_evaluation_methods(self):
        """Test that separate evaluation methods work correctly."""
        evaluator = MockLLMEvaluator()

        # Test weather statements
        sunny_assertion = Assertion("It is sunny today")
        u_component = evaluator._evaluate_verification(sunny_assertion)
        v_component = evaluator._evaluate_refutation(sunny_assertion)

        # Sunny weather should be verifiable but not refutable
        self.assertEqual(u_component, TruthValueComponent.TRUE)
        self.assertEqual(v_component, TruthValueComponent.UNDEFINED)

        # Test that full evaluation matches separate components
        full_result = evaluator.evaluate_bilateral(sunny_assertion)
        self.assertEqual(full_result.u, u_component)
        self.assertEqual(full_result.v, v_component)


if __name__ == "__main__":
    unittest.main()
