import math


def validate_solution(game_data, answer_board):
    problems = []
    board_size = game_data["size"]
    needed_numbers = set(range(1, board_size + 1))

    if not isinstance(answer_board, (list, tuple)) or len(answer_board) != board_size:
        return False, [f"Grid must contain exactly {board_size} rows."]

    for row_num, one_line in enumerate(answer_board):
        if not isinstance(one_line, (list, tuple)) or len(one_line) != board_size:
            return False, [f"Row {row_num+1} must contain exactly {board_size} cells."]
        for col_num, box_number in enumerate(one_line):
            if type(box_number) is not int or box_number not in needed_numbers:
                problems.append(
                    f"Cell ({row_num+1},{col_num+1}) must contain an integer "
                    f"from 1 to {board_size}.")
    if problems:
        return False, problems

    for row_num, one_line in enumerate(answer_board):
        if set(one_line) != needed_numbers:
            problems.append(f"Row {row_num+1} must contain each value "
                            f"1 through {board_size} once.")

    for col_num in range(board_size):
        found_numbers = {answer_board[row_num][col_num]
                         for row_num in range(board_size)}
        if found_numbers != needed_numbers:
            problems.append(f"Column {col_num+1} must contain each value "
                            f"1 through {board_size} once.")

    for (row_num, col_num), fixed_number in game_data["givens"].items():
        if answer_board[row_num][col_num] != fixed_number:
            problems.append(f"Fixed value at ({row_num+1},{col_num+1}) "
                            f"must remain {fixed_number}.")

    for (row_num, col_num), sign in game_data["horizontal_clues"].items():
        left_number = answer_board[row_num][col_num]
        right_number = answer_board[row_num][col_num + 1]
        if (sign == "<" and left_number >= right_number) or \
           (sign == ">" and left_number <= right_number):
            problems.append(f"Horizontal comparison at "
                            f"({row_num+1},{col_num+1}) {sign} "
                            f"({row_num+1},{col_num+2}) fails.")

    for (row_num, col_num), sign in game_data["vertical_clues"].items():
        upper_number = answer_board[row_num][col_num]
        lower_number = answer_board[row_num + 1][col_num]
        if (sign == "∧" and upper_number >= lower_number) or \
           (sign == "∨" and upper_number <= lower_number):
            problems.append(f"Vertical comparison at "
                            f"({row_num+1},{col_num+1}) {sign} "
                            f"({row_num+2},{col_num+1}) fails.")

    return not problems, problems


def validate_solver_result(game_data, solver_answer):
    problems = []
    if solver_answer.status not in ("Solved", "No solution", "Time out"):
        problems.append(f"Unexpected solver status: {solver_answer.status!r}.")

    elapsed_seconds = solver_answer.runtime_seconds
    if type(elapsed_seconds) not in (int, float) or \
       not math.isfinite(elapsed_seconds) or elapsed_seconds < 0:
        problems.append("Runtime must be a finite, nonnegative number.")

    tried_numbers = solver_answer.nodes_explored
    if type(tried_numbers) is not int or tried_numbers < 0:
        problems.append("Nodes explored must be a nonnegative integer.")

    if solver_answer.status == "Solved":
        passed, errors_found = validate_solution(game_data, solver_answer.grid)
        if not passed:
            problems.extend(errors_found)
    elif solver_answer.grid is not None:
        problems.append("Grid must be None unless the status is Solved.")

    return not problems, problems


def find_strict_inequality_cycle(game_data):
    """Return a cycle of cells for an inequality contradiction, or None.

    This checks the puzzle clues *without relying on either search solver*.
    A cycle such as A < B < C < D < A proves that no solution exists.
    Not finding a cycle does NOT prove that a puzzle has a solution.
    """
    next_larger = {}

    def connect(smaller, larger):
        next_larger.setdefault(smaller, []).append(larger)

    for (row, col), sign in game_data['horizontal_clues'].items():
        left, right = (row, col), (row, col + 1)
        if sign == '<':
            connect(left, right)
        else:
            connect(right, left)

    for (row, col), sign in game_data['vertical_clues'].items():
        top, bottom = (row, col), (row + 1, col)
        if sign == '∧':
            connect(top, bottom)
        else:
            connect(bottom, top)

    visited = set()
    active = set()
    trail = []

    def visit(one_cell):
        if one_cell in active:
            return trail[trail.index(one_cell):] + [one_cell]
        if one_cell in visited:
            return None
        active.add(one_cell)
        trail.append(one_cell)
        for next_cell in next_larger.get(one_cell, []):
            found = visit(next_cell)
            if found:
                return found
        trail.pop()
        active.remove(one_cell)
        visited.add(one_cell)
        return None

    for cell in next_larger:
        found = visit(cell)
        if found:
            return found
    return None
