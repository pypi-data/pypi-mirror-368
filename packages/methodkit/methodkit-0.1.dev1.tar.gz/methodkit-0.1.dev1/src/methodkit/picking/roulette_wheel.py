import random
from collections.abc import Sequence
from typing import Generic, TypeVar

__all__ = ["RouletteWheelSelector"]


_T = TypeVar("_T")


class RouletteWheelSelector(Generic[_T]):
    """
    A selector that selects a candidate from a list of candidates based on their fitness values.

    The selector uses a roulette wheel algorithm to select a candidate based on its fitness value. The higher the
    fitness value, the more likely the candidate is selected.
    """

    _candidates: list[_T]
    _fitness_values: list[float]

    def __init__(
        self,
        candidates: list[_T] | Sequence[_T],
        fitness_values: list[float] | Sequence[float] | float | None = None,
    ) -> None:
        """
        Initialize the roulette wheel selector.

        Args:
            candidates:
                The candidates to select from.
            fitness_values:
                The fitness values of the candidates.

        If fitness_values is None, all candidates will have the same fitness value equal to the length of the candidate
        list. If it's a float, all candidates will have the same fitness value equal to the float. Otherwise, the length
        of the fitness_values must be equal to the length of the candidates.
        """
        # Initialize candidates
        if isinstance(candidates, list):
            self._candidates = candidates
        else:
            self._candidates = list(candidates)

        # Initialize (optional) ratios
        if fitness_values is None:
            self._fitness_values = [len(self._candidates)] * len(self._candidates)
        elif isinstance(fitness_values, list):
            self._fitness_values = fitness_values
        elif isinstance(fitness_values, Sequence):
            self._fitness_values = list(fitness_values)
        elif isinstance(fitness_values, float):
            self._fitness_values = [fitness_values] * len(self._candidates)

        # Simple validation
        assert len(self._fitness_values) == len(self._candidates), "there must be one fitness value for each candidate"

    def update(self, index: int, delta_ratio: float = 1.0) -> None:
        """
        Update the fitness value of a candidate at the given index.

        Args:
            index:
                The index of the candidate to update.
            delta_ratio:
                The ratio of the delta to add to the fitness value. Defaults to 1.0.
        """
        self._fitness_values[index] += delta_ratio

    def select(self) -> _T:
        """
        Select a candidate according to the roulette wheel selection algorithm.

        Returns:
            The selected candidate.
        """
        return self.select_indexed()[1]

    def select_indexed(self) -> tuple[int, _T]:
        """
        Select a candidate along with its index according to the roulette wheel selection algorithm.

        Returns:
            A tuple of the index and the selected candidate.
        """
        total = sum(self._fitness_values)
        accumulated_fitness = 0
        target = random.random()
        for i, fitness in enumerate(self._fitness_values):
            accumulated_fitness += fitness
            if accumulated_fitness / total >= target:
                return i, self._candidates[i]
        raise RuntimeError("this should never happen")
