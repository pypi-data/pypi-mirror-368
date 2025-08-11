from functools import cache

import numpy as np

from .smawk import OnlineConcaveMinima
from .types import IntVector, FloatVector


class LineNumbers:
    """Keeps track of the line-numbers of the optimal line breaks.

    This avoids recursively recomputing the line numbers at every cost function call.
    """

    line_numbers: list[int]

    def __init__(self) -> None:
        self.line_numbers = [0]

    def get(self, i: int, cost: OnlineConcaveMinima) -> int:
        while (pos := len(self.line_numbers)) < i + 1:
            line_number = 1 + self.get(cost.index(pos), cost)
            self.line_numbers.append(line_number)
        return self.line_numbers[i]


class TextFragmentsBase:
    """This class is the minimum data structure for text required to run the line breaking (wrapping) algorithm.
    """

    def __init__(
        self,
        widths: FloatVector,
        whitespace_widths: FloatVector,
        penalty_widths: FloatVector,
    ):
        self.widths = widths
        self.whitespace_widths = whitespace_widths
        self.penalty_widths = penalty_widths

    def unpack(self) -> tuple[FloatVector, FloatVector, FloatVector]:
        return self.widths, self.whitespace_widths, self.penalty_widths

    def __len__(self) -> int:
        return len(self.widths)


def wrap(
    fragments: TextFragmentsBase,
    targets: FloatVector = np.array([80.0]),  # maximum length of a wrapped line
    overflow_penalty: float = 10000.0,  # penalize long lines by overpen*(len-target)
    nlinepenalty: float = 1000.0,  # penalize more lines than optimal
    short_last_line_fraction: float = 10.0,  # penalize really short last line
    short_last_line_penalty: float = 25.0,  # by this amount
    hyphen_penalty: float = 15.0,  # penalize hyphenated words
) -> IntVector:
    """Wrap the given text fragments, returning a list of indices representing the breakpoints"""

    widths, whitespace_widths, penalty_widths = fragments.unpack()

    if isinstance(targets, int | float):
        targets = [targets]
    n_targets = len(targets) - 1

    n = len(widths)
    cwidths = np.zeros(n + 1)
    cwidths[1:] = widths.cumsum() + whitespace_widths.cumsum()

    line_numbers = LineNumbers()

    #M = np.zeros((n + 1, n + 1))

    # Define penalty function for breaking on line words[i:j]
    # Below this definition we will set up cost[i] to be the
    # total penalty of all lines up to a break prior to word i.
    @cache
    def penalty(i: int, j: int) -> float:
        if j > n:
            return -i  # concave flag for out of bounds

        line_number = line_numbers.get(i, cost)
        target_width = max(float(targets[min(line_number, n_targets)]), 1.0)

        line_width = (
            cwidths[j] - cwidths[i] - whitespace_widths[j - 1] + max(0, penalty_widths[j - 1])
        )

        c = cost.value(i) + nlinepenalty

        if line_width > target_width:
            overflow = line_width - target_width
            c += (1 + overflow) * overflow_penalty
        elif penalty_widths[j - 1] < 0.0:
            # Negative penalty implies a forced line break.
            # Length of this line is not penalized unless it's too short.
            if line_width < target_width / short_last_line_fraction:
                c += short_last_line_penalty
        else:
            gap = target_width - line_width
            c += gap * gap

        if penalty_widths[j - 1] > 0.0:
            c += hyphen_penalty ** (1 if penalty_widths[i - 1] == 0.0 else 2)

        #M[i, j] = c
        return c

    # Apply concave minima algorithm and backtrack to form lines
    cost = OnlineConcaveMinima(penalty, 0)

    pos = n
    breakpoints = [pos]
    while pos:
        pos = cost.index(pos)
        breakpoints.append(pos)

    return np.array(breakpoints[::-1])
