"""Tests for assertion implementations."""

import unittest
from bilateral_truth.assertions import Assertion


class TestAssertion(unittest.TestCase):
    """Test the Assertion class."""

    def test_simple_predicate(self):
        """Test creating a simple predicate without arguments."""
        assertion = Assertion("P")
        self.assertEqual(assertion.predicate, "P")
        self.assertEqual(assertion.args, ())
        self.assertEqual(assertion.kwargs, {})

    def test_predicate_with_args(self):
        """Test creating a predicate with positional arguments."""
        assertion = Assertion("loves", "alice", "bob")
        self.assertEqual(assertion.predicate, "loves")
        self.assertEqual(assertion.args, ("alice", "bob"))
        self.assertEqual(assertion.kwargs, {})

    def test_predicate_with_kwargs(self):
        """Test creating a predicate with named arguments."""
        assertion = Assertion("distance", subject="alice", object="bob", value=5)
        self.assertEqual(assertion.predicate, "distance")
        self.assertEqual(assertion.args, ())
        self.assertEqual(
            assertion.kwargs, {"subject": "alice", "object": "bob", "value": 5}
        )

    def test_predicate_with_mixed_args(self):
        """Test creating a predicate with both positional and named arguments."""
        assertion = Assertion(
            "relation", "alice", "bob", type="friendship", strength=0.8
        )
        self.assertEqual(assertion.predicate, "relation")
        self.assertEqual(assertion.args, ("alice", "bob"))
        self.assertEqual(assertion.kwargs, {"type": "friendship", "strength": 0.8})

    def test_string_representation(self):
        """Test string representation of assertions."""
        # Simple predicate
        assertion1 = Assertion("P")
        self.assertEqual(str(assertion1), "P")

        # Predicate with args
        assertion2 = Assertion("loves", "alice", "bob")
        self.assertEqual(str(assertion2), "loves(alice, bob)")

        # Predicate with kwargs
        assertion3 = Assertion("distance", value=5, unit="km")
        expected = "distance(unit=km, value=5)"  # sorted by key
        self.assertEqual(str(assertion3), expected)

        # Mixed args
        assertion4 = Assertion("relation", "alice", "bob", type="friendship")
        self.assertEqual(str(assertion4), "relation(alice, bob, type=friendship)")

    def test_equality(self):
        """Test equality comparison between assertions."""
        assertion1 = Assertion("loves", "alice", "bob")
        assertion2 = Assertion("loves", "alice", "bob")
        assertion3 = Assertion("loves", "bob", "alice")  # Different order
        assertion4 = Assertion("likes", "alice", "bob")  # Different predicate

        self.assertEqual(assertion1, assertion2)
        self.assertNotEqual(assertion1, assertion3)
        self.assertNotEqual(assertion1, assertion4)
        self.assertNotEqual(assertion1, "not a assertion")

    def test_kwargs_order_independence(self):
        """Test that kwargs order doesn't affect equality."""
        assertion1 = Assertion("test", a=1, b=2)
        assertion2 = Assertion("test", b=2, a=1)
        self.assertEqual(assertion1, assertion2)

    def test_hashing(self):
        """Test that assertions can be used as dictionary keys."""
        assertion1 = Assertion("loves", "alice", "bob")
        assertion2 = Assertion("loves", "alice", "bob")
        assertion3 = Assertion("loves", "bob", "alice")

        # Equal assertions should have equal hashes
        self.assertEqual(hash(assertion1), hash(assertion2))

        # Test use in dictionary/set
        assertion_set = {assertion1, assertion2, assertion3}
        self.assertEqual(
            len(assertion_set), 2
        )  # assertion1 and assertion2 are the same

        assertion_dict = {assertion1: "true", assertion3: "false"}
        self.assertEqual(
            assertion_dict[assertion2], "true"
        )  # assertion2 equals assertion1

    def test_signature_property(self):
        """Test the signature property."""
        assertion = Assertion("test", "arg1", key="value")
        signature = assertion.signature
        self.assertIsInstance(signature, str)
        self.assertIn("test", signature)
        self.assertIn("arg1", signature)
        self.assertIn("key", signature)


if __name__ == "__main__":
    unittest.main()
