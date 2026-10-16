from dataclasses import dataclass
import time
from csp_model import FutoshikiCSP

DEFAULT_TIMEOUT_SECONDS = 60

class SearchTimedOut(Exception):
    """Raised when the solver reaches its search time limit."""

@dataclass
class SolveResult:
    status: str
    grid: list | None
    runtime_seconds: float
    nodes_explored: int


def solve_backtracking(game_data, timeout_seconds=DEFAULT_TIMEOUT_SECONDS):
    """Row-major search, ascending values, no propagation or heuristics."""
    if timeout_seconds <= 0:
        raise ValueError("The timeout must be greater than zero seconds.")

    started = time.perf_counter()  # includes CSP initialization, not GUI/file loading
    game_rules = FutoshikiCSP(game_data)
    filled_boxes = dict(game_rules.givens)
    empty_boxes = [box for box in game_rules.variables if box not in filled_boxes]
    tried_numbers = 0

    def check_clock():
        if time.perf_counter() - started >= timeout_seconds:
            raise SearchTimedOut()

    def fill_next(box_index):
        nonlocal tried_numbers
        check_clock()
        if box_index == len(empty_boxes):
            return game_rules.is_solution(filled_boxes)
        one_box = empty_boxes[box_index]
        for try_number in sorted(game_rules.domains[one_box]):
            check_clock()
            # One node = one candidate assignment attempted.
            tried_numbers += 1
            if not game_rules.is_consistent(one_box, try_number, filled_boxes):
                continue
            filled_boxes[one_box] = try_number
            if fill_next(box_index + 1):
                return True
            del filled_boxes[one_box]  # Undo a failed choice.
        return False

    finished_board = None
    status = "No solution"
    try:
        check_clock()
        if game_rules.givens_are_consistent() and fill_next(0):
            status = "Solved"
            finished_board = [
                [filled_boxes[(r, c)] for c in range(game_rules.size)]
                for r in range(game_rules.size)
            ]
    except SearchTimedOut:
        status = "Time out"

    return SolveResult(status, finished_board,
                       time.perf_counter() - started, tried_numbers)
