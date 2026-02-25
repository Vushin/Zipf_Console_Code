"""
Utility helpers for Zipf distributions used by simulation modules.

This module keeps all Zipf-specific math and sampling code in one place.
Functions are intentionally explicit and heavily commented for readability.
"""

from __future__ import annotations

import math
from typing import List, Sequence, TypeVar

import numpy as np


# Default exponent used when callers do not provide one.
DEFAULT_ZIPF_S = 2.0

# Generic type so sampling helper can return the same item type as the pool.
T = TypeVar("T")


def zipf_pmf(pool_size: int, exponent_s: float) -> np.ndarray:
    """Return normalized Zipf PMF over ranks 1..pool_size.

    Rank 1 gets the highest mass, rank 2 gets less, and so on.
    """
    ranks = np.arange(1, pool_size + 1, dtype=float)
    unnormalized = 1.0 / (ranks ** exponent_s)
    normalization_constant = unnormalized.sum()
    probabilities = unnormalized / normalization_constant
    return probabilities


def zipf_entropy_bits(pool_size: int, exponent_s: float) -> float:
    """Compute Shannon entropy of Zipf PMF in bits."""
    probabilities = zipf_pmf(pool_size, exponent_s)
    entropy_value = 0.0

    for probability in probabilities:
        probability_value = float(probability)
        if probability_value <= 0.0:
            continue
        entropy_value = entropy_value - (probability_value * math.log2(probability_value))

    return entropy_value


def zipf_rank_weights(pool_size: int, exponent_s: float) -> List[float]:
    """Return Zipf rank probabilities as a plain Python list of floats."""
    probabilities = zipf_pmf(pool_size, exponent_s)
    weights: List[float] = []

    for probability in probabilities:
        weights.append(float(probability))

    return weights


def sample_from_ranked_pool(ranked_pool: Sequence[T], exponent_s: float) -> T:
    """Sample one element from a ranked pool according to Zipf(exponent_s)."""
    probabilities = zipf_pmf(len(ranked_pool), exponent_s)
    sampled_index = int(np.random.choice(len(ranked_pool), p=probabilities))
    return ranked_pool[sampled_index]


def prior_entropy_penalty(source: str, zipf_s: float | None, pool_size: int, default_zipf_s: float = DEFAULT_ZIPF_S) -> float:
    """Return uniform-vs-zipf entropy gap for a ranked pool.

    This helper is kept for compatibility with old analysis paths.
    """
    if source != "zipf":
        return 0.0

    exponent = default_zipf_s if zipf_s is None else zipf_s
    uniform_entropy = math.log2(pool_size)
    zipf_entropy = zipf_entropy_bits(pool_size, exponent)

    penalty = uniform_entropy - zipf_entropy
    if penalty < 0.0:
        return 0.0

    return penalty
