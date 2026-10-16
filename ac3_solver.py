from collections import deque
import time
from backtracking import SolveResult, DEFAULT_TIMEOUT_SECONDS, SearchTimedOut
from csp_model import FutoshikiCSP


def revise(game_rules, number_options, first_box, second_box):
    """Remove any value in Di with no supporting value in Dj (binary CSP)."""
    invalid = set()
    for first_number in number_options[first_box]:
        if not any(game_rules.values_compatible(first_box, first_number,
                                                second_box, second_number)
                   for second_number in number_options[second_box]):
            invalid.add(first_number)
    if invalid:
        number_options[first_box].difference_update(invalid)
        return True
    return False


def enforce_ac3(game_rules, number_options, starting_pairs=None, check_clock=None):
    """Propagate domains until every directed arc has support."""
    if starting_pairs is None:
        queue = deque((box, neighbor) for box in game_rules.variables
                      for neighbor in game_rules.neighbors[box])
    else:
        queue = deque(starting_pairs)

    while queue:
        if check_clock:
            check_clock()
        first_box, second_box = queue.popleft()
        if revise(game_rules, number_options, first_box, second_box):
            if not number_options[first_box]:
                return False
            for other_box in game_rules.neighbors[first_box]:
                if other_box != second_box:
                    queue.append((other_box, first_box))
    return True


def select_mrv_degree(game_rules, number_options):
    """MRV first; on a tie, choose the most unassigned neighbors."""
    open_boxes = [box for box in game_rules.variables if len(number_options[box]) > 1]
    if not open_boxes:
        return None

    def box_rank(one_box):
        remaining_degree = sum(len(number_options[nearby]) > 1
                               for nearby in game_rules.neighbors[one_box])
        return len(number_options[one_box]), -remaining_degree, one_box

    return min(open_boxes, key=box_rank)


def order_lcv(game_rules, number_options, chosen_box):
    """LCV chooses values that remove the fewest remaining neighbor values."""
    neighbors_open = [nearby for nearby in game_rules.neighbors[chosen_box]
                      if len(number_options[nearby]) > 1]

    def eliminated(value):
        return sum(not game_rules.values_compatible(chosen_box, value, nearby, other)
                   for nearby in neighbors_open for other in number_options[nearby])

    return sorted(number_options[chosen_box], key=lambda value: (eliminated(value), value))


def solve_ac3(game_data, timeout_seconds=DEFAULT_TIMEOUT_SECONDS):
    if timeout_seconds <= 0:
        raise ValueError("The timeout must be greater than zero seconds.")

    started = time.perf_counter()
    game_rules = FutoshikiCSP(game_data)
    number_options = {box: set(game_rules.domains[box]) for box in game_rules.variables}
    tried_numbers = 0

    def check_clock():
        if time.perf_counter() - started >= timeout_seconds:
            raise SearchTimedOut()

    def try_choices(options_now):
        nonlocal tried_numbers
        check_clock()
        selected = select_mrv_degree(game_rules, options_now)
        if selected is None:
            filled = {box: next(iter(options_now[box])) for box in game_rules.variables}
            return filled if game_rules.is_solution(filled) else None

        for number in order_lcv(game_rules, options_now, selected):
            check_clock()
            tried_numbers += 1  # Node = a tried assignment to an unassigned cell.
            # Copy EVERY domain: failed branches never change their parent's sets.
            branch_options = {box: set(options_now[box]) for box in game_rules.variables}
            branch_options[selected] = {number}
            # Xi's domain changed; revise arcs (neighbor, Xi) to propagate.
            affected = [(nearby, selected) for nearby in game_rules.neighbors[selected]]
            if enforce_ac3(game_rules, branch_options, affected, check_clock):
                answer = try_choices(branch_options)
                if answer is not None:
                    return answer
        return None

    final_status = "No solution"
    final_board = None
    try:
        check_clock()
        if game_rules.givens_are_consistent() and enforce_ac3(
                game_rules, number_options, check_clock=check_clock):
            filled = try_choices(number_options)
            if filled is not None:
                final_status = "Solved"
                final_board = [[filled[(r, c)] for c in range(game_rules.size)]
                               for r in range(game_rules.size)]
    except SearchTimedOut:
        final_status = "Time out"

    return SolveResult(final_status, final_board,
                       time.perf_counter() - started, tried_numbers)
