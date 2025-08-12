"""
Implementation of the ζ (zeta) and ζ_c (zeta_c) functions.

The ζ function provides bilateral factuality evaluation of atomic formulas,
while ζ_c adds persistent caching for improved performance.
"""

from typing import Dict, Callable, Optional, Union, Tuple, Any
from .assertions import Assertion
from .truth_values import GeneralizedTruthValue


class ZetaCache:
    """
    Persistent, immutable-style cache for ζ_c function.

    Implements the cache c used in the ζ_c definition:
    ζ_c(φ) = c(φ) if φ ∈ dom(c), else ζ(φ) and c := c ∪ {(φ, ζ(φ))}
    """

    def __init__(self):
        self._cache: Dict[Union[Assertion, Tuple[Any, ...]], GeneralizedTruthValue] = {}

    def __contains__(self, key: Union[Assertion, Tuple[Any, ...]]) -> bool:
        """Check if key is in the domain of the cache."""
        return key in self._cache

    def get(
        self, key: Union[Assertion, Tuple[Any, ...]]
    ) -> Optional[GeneralizedTruthValue]:
        """Get cached value for key, or None if not cached."""
        return self._cache.get(key)

    def update(
        self, key: Union[Assertion, Tuple[Any, ...]], value: GeneralizedTruthValue
    ) -> "ZetaCache":
        """
        Return a new cache with the key-value pair added.

        Note: In practice, we modify the existing cache for efficiency,
        but the interface maintains the mathematical abstraction of
        immutable cache updates.
        """
        self._cache[key] = value
        return self

    def __len__(self) -> int:
        """Return the number of cached entries."""
        return len(self._cache)

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()


def zeta(
    assertion: Assertion, evaluator: Callable[[Assertion], GeneralizedTruthValue]
) -> GeneralizedTruthValue:
    """
    The base ζ function for bilateral factuality evaluation.

    This function performs bilateral evaluation by assessing both verifiability (u)
    and refutability (v) of assertions using LLM-based evaluation.

    Args:
        assertion: The assertion φ ∈ ℒ_AT to evaluate
        evaluator: LLM evaluator function that performs bilateral assessment.
                  Must be provided - no default evaluation.

    Returns:
        A GeneralizedTruthValue <u,v> representing the bilateral evaluation
    """
    return evaluator(assertion)


# Global cache instance
_global_cache = ZetaCache()


def zeta_c(
    assertion: Assertion,
    evaluator: Callable[[Assertion], GeneralizedTruthValue],
    cache: Optional[ZetaCache] = None,
    samples: int = 1,
    tiebreak_strategy: str = "random",
) -> GeneralizedTruthValue:
    """
    The cached ζ_c function: ℒ_AT → 𝒱³ × 𝒱³

    Implements: ζ_c(φ) = c(φ) if φ ∈ dom(c), else ζ(φ) and c := c ∪ {(φ, ζ(φ))}

    Args:
        assertion: The assertion φ ∈ ℒ_AT to evaluate
        evaluator: LLM evaluator function for bilateral assessment. Required.
        cache: Optional cache instance. If None, uses global cache.
        samples: Number of samples for majority voting (default: 1)
        tiebreak_strategy: Strategy for breaking ties ("random", "pessimistic", "optimistic")

    Returns:
        A GeneralizedTruthValue <u,v> from cache or computed via ζ
    """
    if cache is None:
        cache = _global_cache

    # Cache key is just the assertion φ as per Definition 3.5
    # Sampling is handled within ζ(φ), not in the cache key
    cache_key = assertion

    # Check if result is in cache domain: φ ∈ dom(c)
    if cache_key in cache:
        cached_result = cache.get(cache_key)  # Return c(φ)
        assert cached_result is not None  # Should never be None since key exists
        return cached_result

    # Compute ζ(φ) with sampling - this is the ζ function call from Definition 3.5
    if hasattr(evaluator, "evaluate_bilateral"):
        # New interface with sampling support
        truth_value = evaluator.evaluate_bilateral(assertion, samples)
    else:
        # Legacy interface - single evaluation only
        if samples > 1:
            print(
                "Warning: Evaluator doesn't support sampling. Using single evaluation."
            )
        truth_value = evaluator(assertion)

    # Update cache: c := c ∪ {(φ, ζ(φ))}
    cache.update(cache_key, truth_value)

    return truth_value


def clear_cache() -> None:
    """Clear the global cache."""
    _global_cache.clear()


def get_cache_size() -> int:
    """Get the number of entries in the global cache."""
    return len(_global_cache)
