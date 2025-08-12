"""Tests for truth value implementations."""

import unittest
from bilateral_truth.truth_values import (
    TruthValueComponent,
    GeneralizedTruthValue,
    EpistemicPolicy,
)


class TestTruthValueComponent(unittest.TestCase):
    """Test the TruthValueComponent enum."""

    def test_truth_value_components(self):
        """Test that all three components exist with correct values."""
        self.assertEqual(TruthValueComponent.TRUE.value, "t")
        self.assertEqual(TruthValueComponent.UNDEFINED.value, "e")
        self.assertEqual(TruthValueComponent.FALSE.value, "f")


class TestGeneralizedTruthValue(unittest.TestCase):
    """Test the GeneralizedTruthValue class."""

    def test_initialization(self):
        """Test creating generalized truth values."""
        gtv = GeneralizedTruthValue(TruthValueComponent.TRUE, TruthValueComponent.FALSE)
        self.assertEqual(gtv.u, TruthValueComponent.TRUE)
        self.assertEqual(gtv.v, TruthValueComponent.FALSE)

    def test_components_property(self):
        """Test the components property returns correct tuple."""
        gtv = GeneralizedTruthValue(
            TruthValueComponent.UNDEFINED, TruthValueComponent.TRUE
        )
        self.assertEqual(
            gtv.components, (TruthValueComponent.UNDEFINED, TruthValueComponent.TRUE)
        )

    def test_string_representation(self):
        """Test string representation."""
        gtv = GeneralizedTruthValue(TruthValueComponent.TRUE, TruthValueComponent.FALSE)
        self.assertEqual(str(gtv), "<t,f>")
        self.assertEqual(repr(gtv), "<t,f>")

    def test_equality(self):
        """Test equality comparison."""
        gtv1 = GeneralizedTruthValue(
            TruthValueComponent.TRUE, TruthValueComponent.FALSE
        )
        gtv2 = GeneralizedTruthValue(
            TruthValueComponent.TRUE, TruthValueComponent.FALSE
        )
        gtv3 = GeneralizedTruthValue(
            TruthValueComponent.FALSE, TruthValueComponent.TRUE
        )

        self.assertEqual(gtv1, gtv2)
        self.assertNotEqual(gtv1, gtv3)
        self.assertNotEqual(gtv1, "not a truth value")

    def test_hashing(self):
        """Test that truth values can be used as dictionary keys."""
        gtv1 = GeneralizedTruthValue(
            TruthValueComponent.TRUE, TruthValueComponent.FALSE
        )
        gtv2 = GeneralizedTruthValue(
            TruthValueComponent.TRUE, TruthValueComponent.FALSE
        )
        gtv3 = GeneralizedTruthValue(
            TruthValueComponent.FALSE, TruthValueComponent.TRUE
        )

        # Equal objects should have equal hashes
        self.assertEqual(hash(gtv1), hash(gtv2))

        # Test use in dictionary
        truth_dict = {gtv1: "classical true", gtv3: "classical false"}
        self.assertEqual(truth_dict[gtv2], "classical true")  # gtv2 equals gtv1

    def test_classical_projection(self):
        """Test classical projection with designated/anti-designated value sets."""
        # Classical true: <t,f> → t
        classical_true = GeneralizedTruthValue(
            TruthValueComponent.TRUE, TruthValueComponent.FALSE
        )
        self.assertEqual(
            classical_true.project(EpistemicPolicy.CLASSICAL), TruthValueComponent.TRUE
        )

        # Classical false: <f,t> → f
        classical_false = GeneralizedTruthValue(
            TruthValueComponent.FALSE, TruthValueComponent.TRUE
        )
        self.assertEqual(
            classical_false.project(EpistemicPolicy.CLASSICAL),
            TruthValueComponent.FALSE,
        )

        # All other combinations → e
        other_combinations = [
            GeneralizedTruthValue(TruthValueComponent.TRUE, TruthValueComponent.TRUE),
            GeneralizedTruthValue(
                TruthValueComponent.TRUE, TruthValueComponent.UNDEFINED
            ),
            GeneralizedTruthValue(TruthValueComponent.FALSE, TruthValueComponent.FALSE),
            GeneralizedTruthValue(
                TruthValueComponent.FALSE, TruthValueComponent.UNDEFINED
            ),
            GeneralizedTruthValue(
                TruthValueComponent.UNDEFINED, TruthValueComponent.TRUE
            ),
            GeneralizedTruthValue(
                TruthValueComponent.UNDEFINED, TruthValueComponent.FALSE
            ),
            GeneralizedTruthValue(
                TruthValueComponent.UNDEFINED, TruthValueComponent.UNDEFINED
            ),
        ]
        for gtv in other_combinations:
            self.assertEqual(
                gtv.project(EpistemicPolicy.CLASSICAL), TruthValueComponent.UNDEFINED
            )

    def test_paraconsistent_projection(self):
        """Test paraconsistent projection (allows contradictions)."""
        # Designated: {<u,v> | u=t} → t
        paraconsistent_true_cases = [
            GeneralizedTruthValue(TruthValueComponent.TRUE, TruthValueComponent.TRUE),
            GeneralizedTruthValue(TruthValueComponent.TRUE, TruthValueComponent.FALSE),
            GeneralizedTruthValue(
                TruthValueComponent.TRUE, TruthValueComponent.UNDEFINED
            ),
        ]
        for gtv in paraconsistent_true_cases:
            self.assertEqual(
                gtv.project(EpistemicPolicy.PARACONSISTENT), TruthValueComponent.TRUE
            )

        # Anti-designated: {<u,v> | v=t} → f
        paraconsistent_false_cases = [
            GeneralizedTruthValue(TruthValueComponent.FALSE, TruthValueComponent.TRUE),
            GeneralizedTruthValue(
                TruthValueComponent.UNDEFINED, TruthValueComponent.TRUE
            ),
        ]
        for gtv in paraconsistent_false_cases:
            self.assertEqual(
                gtv.project(EpistemicPolicy.PARACONSISTENT), TruthValueComponent.FALSE
            )

        # Neither (all others) → e
        paraconsistent_undefined_cases = [
            GeneralizedTruthValue(TruthValueComponent.FALSE, TruthValueComponent.FALSE),
            GeneralizedTruthValue(
                TruthValueComponent.FALSE, TruthValueComponent.UNDEFINED
            ),
            GeneralizedTruthValue(
                TruthValueComponent.UNDEFINED, TruthValueComponent.FALSE
            ),
            GeneralizedTruthValue(
                TruthValueComponent.UNDEFINED, TruthValueComponent.UNDEFINED
            ),
        ]
        for gtv in paraconsistent_undefined_cases:
            self.assertEqual(
                gtv.project(EpistemicPolicy.PARACONSISTENT),
                TruthValueComponent.UNDEFINED,
            )

    def test_paracomplete_projection(self):
        """Test paracomplete projection (allows truth value gaps)."""
        # Designated: {<u,v> | v=f} → t
        paracomplete_true_cases = [
            GeneralizedTruthValue(TruthValueComponent.TRUE, TruthValueComponent.FALSE),
            GeneralizedTruthValue(TruthValueComponent.FALSE, TruthValueComponent.FALSE),
            GeneralizedTruthValue(
                TruthValueComponent.UNDEFINED, TruthValueComponent.FALSE
            ),
        ]
        for gtv in paracomplete_true_cases:
            self.assertEqual(
                gtv.project(EpistemicPolicy.PARACOMPLETE), TruthValueComponent.TRUE
            )

        # Anti-designated: {<u,v> | u=f} → f
        paracomplete_false_cases = [
            GeneralizedTruthValue(TruthValueComponent.FALSE, TruthValueComponent.TRUE),
            GeneralizedTruthValue(
                TruthValueComponent.FALSE, TruthValueComponent.UNDEFINED
            ),
        ]
        for gtv in paracomplete_false_cases:
            self.assertEqual(
                gtv.project(EpistemicPolicy.PARACOMPLETE), TruthValueComponent.FALSE
            )

        # Neither (all others) → e
        paracomplete_undefined_cases = [
            GeneralizedTruthValue(TruthValueComponent.TRUE, TruthValueComponent.TRUE),
            GeneralizedTruthValue(
                TruthValueComponent.TRUE, TruthValueComponent.UNDEFINED
            ),
            GeneralizedTruthValue(
                TruthValueComponent.UNDEFINED, TruthValueComponent.TRUE
            ),
            GeneralizedTruthValue(
                TruthValueComponent.UNDEFINED, TruthValueComponent.UNDEFINED
            ),
        ]
        for gtv in paracomplete_undefined_cases:
            self.assertEqual(
                gtv.project(EpistemicPolicy.PARACOMPLETE), TruthValueComponent.UNDEFINED
            )


if __name__ == "__main__":
    unittest.main()
