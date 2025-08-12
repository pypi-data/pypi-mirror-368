import unittest
from collections import Counter
from collections.abc import Sequence
from typing import ClassVar

from scipy.stats import chisquare  # pyright: ignore[reportUnknownVariableType]

from methodkit.picking.roulette_wheel import RouletteWheelSelector


class RouletteWheelSelectorTestCase(unittest.TestCase):
    # Randomly selected numbers
    _CANDIDATE_COUNT: ClassVar[int] = 5
    _SELECT_TIMES: ClassVar[int] = 10000

    _selector: RouletteWheelSelector[None]

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self._selector = RouletteWheelSelector([None] * self._CANDIDATE_COUNT)

    def test_roulette_wheel(self) -> None:
        """
        Test whether the roulette wheel works correctly.

        In this case, we do not update the fitness values, and the chosen ones should conform to the uniform
        distribution. We use scipy to verify the result.
        """
        values: list[int] = []
        for _ in range(self._SELECT_TIMES):
            index, _ = self._selector.select_indexed()
            values.append(index)
        self.assertTrue(_is_uniform_distribution(values))


def _is_uniform_distribution(values: Sequence[int]) -> bool:
    """
    Tests whether the given values are uniformly distributed.

    Args:
        values: The values to test.
    """
    observation = list(Counter(values).values())
    expectation = [len(values) / len(observation)] * len(observation)
    result = chisquare(observation, expectation)
    return result.pvalue.item() > 0.05
