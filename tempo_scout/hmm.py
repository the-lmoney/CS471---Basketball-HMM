"""Validated, immutable two-state HMM with sequential forward filtering.

State order is FAST, CONTROLLED; emission columns are QUICK, NORMAL, LONG.
Each filtering call starts a new episode and uses only observations seen so far.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Sequence


STATES = ("FAST", "CONTROLLED")
OBSERVATIONS = ("QUICK", "NORMAL", "LONG")
Belief = tuple[float, float]
_SUM_TOLERANCE = 1e-12


def _distribution(
    values: Iterable[float], length: int, name: str
) -> tuple[float, ...]:
    """Copy and validate a probability vector without silently fixing it."""
    try:
        copied = tuple(values)
    except TypeError as error:
        raise ValueError(f"{name} must be a probability vector.") from error
    if len(copied) != length:
        raise ValueError(f"{name} must contain exactly {length} probabilities.")
    for value in copied:
        try:
            valid = math.isfinite(value) and 0.0 <= value <= 1.0
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError(f"{name} probabilities must be finite numbers in [0, 1].") from error
        if not valid:
            raise ValueError(f"{name} probabilities must be finite numbers in [0, 1].")
    result = tuple(float(value) for value in copied)
    if not math.isclose(math.fsum(result), 1.0, rel_tol=0.0, abs_tol=_SUM_TOLERANCE):
        raise ValueError(f"{name} probabilities must sum to 1.")
    return result


def _matrix(
    values: Iterable[Iterable[float]], rows: int, columns: int, name: str
) -> tuple[tuple[float, ...], ...]:
    try:
        copied = tuple(values)
    except TypeError as error:
        raise ValueError(f"{name} must be a probability matrix.") from error
    if len(copied) != rows:
        raise ValueError(f"{name} must contain exactly {rows} rows.")
    return tuple(
        _distribution(row, columns, f"{name} row {index}")
        for index, row in enumerate(copied)
    )


@dataclass(frozen=True, slots=True)
class DiscreteHMM:
    """A fixed-parameter HMM; model validation also supports correctness fixtures.

    List inputs are copied to tuples so a caller cannot later mutate a validated
    model. The instance stores parameters only, never an episode's posterior.
    """

    initial: Belief = (0.50, 0.50)
    transition: tuple[Belief, Belief] = ((0.80, 0.20), (0.20, 0.80))
    emission: tuple[tuple[float, float, float], tuple[float, float, float]] = (
        (0.60, 0.30, 0.10),
        (0.10, 0.30, 0.60),
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "initial", _distribution(self.initial, 2, "Initial distribution"))
        object.__setattr__(self, "transition", _matrix(self.transition, 2, 2, "Transition matrix"))
        object.__setattr__(self, "emission", _matrix(self.emission, 2, 3, "Emission matrix"))

    def predict_next_state(self, posterior: Sequence[float]) -> Belief:
        """Apply one transition to a valid current-state posterior."""
        belief = _distribution(posterior, 2, "Posterior")
        fast = math.fsum(belief[i] * self.transition[i][0] for i in range(2))
        controlled = math.fsum(belief[i] * self.transition[i][1] for i in range(2))
        return (fast, controlled)

    def filter_sequence(self, observations: Iterable[str]) -> tuple[Belief, ...]:
        """Return P(state_t | observations_1..t) after each observation.

        The first observation updates the initial distribution directly. Every
        later observation follows one transition and one emission update.
        Normalizing each step avoids multiplying a whole episode's likelihoods.
        """
        try:
            iterator = iter(observations)
        except TypeError as error:
            raise ValueError("Observations must be a nonempty iterable of symbols.") from error
        results: list[Belief] = []
        for step, observation in enumerate(iterator, start=1):
            if not isinstance(observation, str) or observation not in OBSERVATIONS:
                raise ValueError(
                    f"Invalid observation {observation!r} at step {step}; "
                    f"expected one of {', '.join(OBSERVATIONS)}."
                )
            column = OBSERVATIONS.index(observation)
            prior = self.initial if not results else self.predict_next_state(results[-1])
            weights = tuple(prior[j] * self.emission[j][column] for j in range(2))
            normalization = math.fsum(weights)
            if not math.isfinite(normalization) or normalization <= 0.0:
                raise ValueError(
                    f"Cannot normalize posterior at step {step}: observation "
                    f"{observation!r} has zero or nonfinite probability under this model."
                )
            results.append((weights[0] / normalization, weights[1] / normalization))
        if not results:
            raise ValueError("Observation sequence must not be empty.")
        return tuple(results)

    def predict_next_quick(self, posterior: Sequence[float]) -> float:
        """Forecast the next possession, including its state transition."""
        next_state = self.predict_next_state(posterior)
        quick_column = OBSERVATIONS.index("QUICK")
        return math.fsum(next_state[j] * self.emission[j][quick_column] for j in range(2))


DEFAULT_MODEL = DiscreteHMM()
