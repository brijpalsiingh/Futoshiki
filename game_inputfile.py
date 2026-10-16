import tkinter as tk


def display_fixed_numbers(board_boxes, fixed_places):
    board_size = len(board_boxes)
    if any(len(one_line) != board_size for one_line in board_boxes):
        raise ValueError("Puzzle board must be square")

    for (row_num, col_num), fixed_number in fixed_places.items():
        if not (0 <= row_num < board_size and 0 <= col_num < board_size):
            raise ValueError("Fixed number is outside the board")
        if type(fixed_number) is not int or not 1 <= fixed_number <= board_size:
            raise ValueError("Fixed number is not in the allowed range")

    for (row_num, col_num), fixed_number in fixed_places.items():
        one_box = board_boxes[row_num][col_num]
        one_box.config(state="normal")
        one_box.delete(0, tk.END)
        one_box.insert(0, str(fixed_number))
        one_box.config(state="readonly", readonlybackground="#DCEBFA")


def display_inequalities(puzzle_area, board_size, left_right, up_down):
    side_arrows = {}
    up_arrows = {}
    area_colour = puzzle_area.cget("bg")
    arrow_font = 18 if board_size <= 6 else 15

    for row_num in range(board_size):
        for col_num in range(board_size - 1):
            arrow_sign = left_right.get((row_num, col_num), " ")
            arrow = tk.Label(puzzle_area, text=arrow_sign,
                             font=("Times New Roman", arrow_font, "bold"),
                             bg=area_colour)
            arrow.grid(row=2 * row_num, column=2 * col_num + 1)
            side_arrows[(row_num, col_num)] = arrow

    for row_num in range(board_size - 1):
        for col_num in range(board_size):
            arrow_sign = up_down.get((row_num, col_num), " ")
            arrow = tk.Label(puzzle_area, text=arrow_sign,
                             font=("Times New Roman", arrow_font, "bold"),
                             bg=area_colour)
            arrow.grid(row=2 * row_num + 1, column=2 * col_num)
            up_arrows[(row_num, col_num)] = arrow

    return side_arrows, up_arrows


def display_game_input(puzzle_area, board_boxes, game_data):
    display_fixed_numbers(board_boxes, game_data["givens"])
    return display_inequalities(puzzle_area, game_data["size"],
                                game_data["horizontal_clues"],
                                game_data["vertical_clues"])
