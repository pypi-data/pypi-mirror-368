"""Tests for zeta and zeta_c function implementations."""

import unittest
import pytest
from bilateral_truth.assertions import Assertion
from bilateral_truth.truth_values import GeneralizedTruthValue, TruthValueComponent
from bilateral_truth.zeta_function import (
    zeta,
    zeta_c,
    ZetaCache,
    clear_cache,
    get_cache_size,
)


class TestZetaCache(unittest.TestCase):
    """Test the ZetaCache class."""

    def setUp(self):
        """Set up test fixtures."""
        self.cache = ZetaCache()
        self.assertion = Assertion("test")
        self.truth_value = GeneralizedTruthValue(
            TruthValueComponent.TRUE, TruthValueComponent.FALSE
        )

    def test_empty_cache(self):
        """Test empty cache behavior."""
        self.assertFalse(self.assertion in self.cache)
        self.assertIsNone(self.cache.get(self.assertion))
        self.assertEqual(len(self.cache), 0)

    def test_cache_update_and_retrieval(self):
        """Test adding to and retrieving from cache."""
        # Update cache
        updated_cache = self.cache.update(self.assertion, self.truth_value)
        self.assertEqual(updated_cache, self.cache)  # Should return same instance

        # Check cache contents
        self.assertTrue(self.assertion in self.cache)
        self.assertEqual(self.cache.get(self.assertion), self.truth_value)
        self.assertEqual(len(self.cache), 1)

    def test_cache_clear(self):
        """Test clearing the cache."""
        self.cache.update(self.assertion, self.truth_value)
        self.assertEqual(len(self.cache), 1)

        self.cache.clear()
        self.assertEqual(len(self.cache), 0)
        self.assertFalse(self.assertion in self.cache)


class TestZetaFunction(unittest.TestCase):
    """Test the zeta function."""

    def test_zeta_requires_evaluator(self):
        """Test that zeta function requires an evaluator."""
        assertion = Assertion("test")

        # Should raise TypeError when no evaluator provided
        with self.assertRaises(TypeError):
            zeta(assertion)

    def test_custom_evaluator(self):
        """Test using a custom evaluator function."""

        def custom_evaluator(assertion):
            if assertion.predicate == "always_true":
                return GeneralizedTruthValue(
                    TruthValueComponent.TRUE, TruthValueComponent.FALSE
                )
            else:
                return GeneralizedTruthValue(
                    TruthValueComponent.FALSE, TruthValueComponent.TRUE
                )

        assertion1 = Assertion("always_true")
        assertion2 = Assertion("anything_else")

        result1 = zeta(assertion1, custom_evaluator)
        result2 = zeta(assertion2, custom_evaluator)

        self.assertEqual(
            result1,
            GeneralizedTruthValue(TruthValueComponent.TRUE, TruthValueComponent.FALSE),
        )
        self.assertEqual(
            result2,
            GeneralizedTruthValue(TruthValueComponent.FALSE, TruthValueComponent.TRUE),
        )


class TestZetaCFunction(unittest.TestCase):
    """Test the zeta_c cached function."""

    def setUp(self):
        """Set up test fixtures."""
        clear_cache()  # Start with clean global cache

    def tearDown(self):
        """Clean up after tests."""
        clear_cache()

    def test_first_evaluation_caches_result(self):
        """Test that first evaluation caches the result."""
        assertion = Assertion("test")

        def test_evaluator(f):
            return GeneralizedTruthValue(
                TruthValueComponent.TRUE, TruthValueComponent.FALSE
            )

        # First call should compute and cache
        self.assertEqual(get_cache_size(), 0)
        result1 = zeta_c(assertion, test_evaluator)
        self.assertEqual(get_cache_size(), 1)
        self.assertEqual(
            result1,
            GeneralizedTruthValue(TruthValueComponent.TRUE, TruthValueComponent.FALSE),
        )

    def test_second_evaluation_uses_cache(self):
        """Test that second evaluation uses cached result."""
        assertion = Assertion("test")

        # Custom evaluator that should only be called once
        call_count = 0

        def counting_evaluator(f):
            nonlocal call_count
            call_count += 1
            return GeneralizedTruthValue(
                TruthValueComponent.FALSE, TruthValueComponent.TRUE
            )

        # First call
        result1 = zeta_c(assertion, counting_evaluator)
        self.assertEqual(call_count, 1)
        self.assertEqual(
            result1,
            GeneralizedTruthValue(TruthValueComponent.FALSE, TruthValueComponent.TRUE),
        )

        # Second call should use cache, not call evaluator again
        result2 = zeta_c(assertion, counting_evaluator)
        self.assertEqual(call_count, 1)  # Should still be 1
        self.assertEqual(
            result2,
            GeneralizedTruthValue(TruthValueComponent.FALSE, TruthValueComponent.TRUE),
        )
        self.assertEqual(result1, result2)

    def test_different_assertions_evaluated_separately(self):
        """Test that different assertions are evaluated and cached separately."""
        assertion1 = Assertion("test1")
        assertion2 = Assertion("test2")

        def test_evaluator(f):
            if f.predicate == "test1":
                return GeneralizedTruthValue(
                    TruthValueComponent.TRUE, TruthValueComponent.FALSE
                )
            else:
                return GeneralizedTruthValue(
                    TruthValueComponent.FALSE, TruthValueComponent.TRUE
                )

        result1 = zeta_c(assertion1, test_evaluator)
        result2 = zeta_c(assertion2, test_evaluator)

        self.assertEqual(get_cache_size(), 2)
        self.assertEqual(
            result1,
            GeneralizedTruthValue(TruthValueComponent.TRUE, TruthValueComponent.FALSE),
        )
        self.assertEqual(
            result2,
            GeneralizedTruthValue(TruthValueComponent.FALSE, TruthValueComponent.TRUE),
        )

    def test_custom_cache(self):
        """Test using a custom cache instance."""
        custom_cache = ZetaCache()
        assertion = Assertion("test")

        def test_evaluator(f):
            return GeneralizedTruthValue(
                TruthValueComponent.UNDEFINED, TruthValueComponent.UNDEFINED
            )

        # Use custom cache
        result1 = zeta_c(assertion, test_evaluator, cache=custom_cache)
        self.assertEqual(len(custom_cache), 1)
        self.assertEqual(get_cache_size(), 0)  # Global cache should be empty
        self.assertIsInstance(result1, GeneralizedTruthValue)

        # Use global cache
        result2 = zeta_c(assertion, test_evaluator)
        self.assertEqual(len(custom_cache), 1)
        self.assertEqual(get_cache_size(), 1)  # Now global cache has one entry
        self.assertIsInstance(result2, GeneralizedTruthValue)

    def test_cache_persistence_across_calls(self):
        """Test that cache persists across multiple function calls."""
        assertions = [Assertion(f"pred_{i}") for i in range(5)]

        def test_evaluator(f):
            return GeneralizedTruthValue(
                TruthValueComponent.UNDEFINED, TruthValueComponent.UNDEFINED
            )

        # Evaluate all assertions
        results1 = [zeta_c(f, test_evaluator) for f in assertions]
        self.assertEqual(get_cache_size(), 5)

        # Evaluate again, should get same results from cache
        results2 = [zeta_c(f, test_evaluator) for f in assertions]
        self.assertEqual(get_cache_size(), 5)  # No new entries
        self.assertEqual(results1, results2)


@pytest.mark.integration
class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""

    def setUp(self):
        """Set up test fixtures."""
        clear_cache()

    def tearDown(self):
        """Clean up after tests."""
        clear_cache()

    def test_complete_workflow(self):
        """Test a complete workflow with multiple assertions and evaluations."""
        # Create some test assertions
        assertions = [
            Assertion("statement1"),
            Assertion("statement2"),
            Assertion("statement3"),
            Assertion("loves", "alice", "bob"),
            Assertion("distance", start="A", end="B", value=10),
        ]

        def test_evaluator(f):
            if f.predicate == "statement1":
                return GeneralizedTruthValue(
                    TruthValueComponent.TRUE, TruthValueComponent.FALSE
                )
            elif f.predicate == "statement2":
                return GeneralizedTruthValue(
                    TruthValueComponent.FALSE, TruthValueComponent.TRUE
                )
            else:
                return GeneralizedTruthValue(
                    TruthValueComponent.UNDEFINED, TruthValueComponent.UNDEFINED
                )

        # First round of evaluations
        results1 = []
        for assertion in assertions:
            result = zeta_c(assertion, test_evaluator)
            results1.append(result)
            self.assertIsInstance(result, GeneralizedTruthValue)

        self.assertEqual(get_cache_size(), len(assertions))

        # Second round should use cache
        results2 = [zeta_c(f, test_evaluator) for f in assertions]
        self.assertEqual(results1, results2)
        self.assertEqual(get_cache_size(), len(assertions))  # No new entries

        # Verify specific expected results
        self.assertEqual(
            results1[0],
            GeneralizedTruthValue(TruthValueComponent.TRUE, TruthValueComponent.FALSE),
        )  # "statement1"
        self.assertEqual(
            results1[1],
            GeneralizedTruthValue(TruthValueComponent.FALSE, TruthValueComponent.TRUE),
        )  # "statement2"
        self.assertEqual(
            results1[2],
            GeneralizedTruthValue(
                TruthValueComponent.UNDEFINED, TruthValueComponent.UNDEFINED
            ),
        )  # "statement3"


if __name__ == "__main__":
    unittest.main()
