"""
Assertion representation for the ζ_c function implementation.

Provides a simple representation of assertions in ℒ_AT
(the language of atomic assertions).
"""

from typing import Any


class Assertion:
    """
    Represents an assertion φ ∈ ℒ_AT

    An assertion is the basic unit of logical evaluation,
    consisting of a predicate/statement and optional arguments.
    """

    def __init__(self, predicate: str, *args: Any, **kwargs: Any):
        """
        Initialize an assertion.

        Args:
            predicate: The predicate name/symbol or natural language statement
            *args: Positional arguments to the predicate
            **kwargs: Named arguments to the predicate
        """
        self.predicate = predicate
        self.args = args
        self.kwargs = kwargs

        # Create a normalized representation for hashing and equality
        self._normalized = (predicate, args, tuple(sorted(kwargs.items())))

    def __repr__(self) -> str:
        """String representation of the assertion."""
        parts = [self.predicate]

        if self.args:
            parts.extend(str(arg) for arg in self.args)

        if self.kwargs:
            parts.extend(f"{k}={v}" for k, v in sorted(self.kwargs.items()))

        return (
            f"{self.predicate}({', '.join(map(str, self.args + tuple(f'{k}={v}' for k, v in sorted(self.kwargs.items()))))})"
            if self.args or self.kwargs
            else self.predicate
        )

    def __eq__(self, other) -> bool:
        """Check equality with another assertion."""
        if not isinstance(other, Assertion):
            return False
        return self._normalized == other._normalized

    def __hash__(self) -> int:
        """Hash function for use in dictionaries/sets."""
        return hash(self._normalized)

    @property
    def signature(self) -> str:
        """Return a string signature of this assertion for debugging."""
        return str(self._normalized)
