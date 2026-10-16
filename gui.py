import tkinter as tk


WINDOW_COLOUR = "#F5F7FA"
HEADING_COLOUR = "#17365D"
MAIN_FONT = ("Times New Roman", 12)


def create_gui():
    main_window = tk.Tk()
    main_window.title("FUTOSHIKI PUZZLE")
    main_window.geometry("1180x720")
    main_window.minsize(980, 650)
    main_window.configure(bg=WINDOW_COLOUR)

    heading = tk.Label(
        main_window, text="FUTOSHIKI PUZZLE",
        font=("Times New Roman", 22, "bold"),
        bg=WINDOW_COLOUR, fg=HEADING_COLOUR
    )
    heading.pack(pady=(16, 7))

    # The left and right panels stay beside the board, not above or below it.
    page_area = tk.Frame(main_window, bg=WINDOW_COLOUR)
    page_area.pack(fill="both", expand=True, padx=16, pady=(5, 12))
    page_area.grid_columnconfigure(0, minsize=380, weight=0)
    page_area.grid_columnconfigure(1, weight=1)
    page_area.grid_columnconfigure(2, minsize=230, weight=0)
    page_area.grid_rowconfigure(0, weight=1)

    # LEFT: Current result and side-by-side solver comparison.
    stats_area = tk.LabelFrame(
        page_area, text="Statistics", font=("Times New Roman", 14, "bold"),
        fg=HEADING_COLOUR, bg=WINDOW_COLOUR, padx=12, pady=14
    )
    stats_area.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

    message_label = tk.Label(
        stats_area, text="Status: Ready - load a TXT puzzle",
        font=MAIN_FONT, bg=WINDOW_COLOUR, fg=HEADING_COLOUR,
        wraplength=210, justify="left", anchor="w"
    )
    message_label.pack(fill="x", anchor="w", pady=(4, 16))

    time_label = tk.Label(
        stats_area, text="Runtime: --", font=MAIN_FONT,
        bg=WINDOW_COLOUR, justify="left", anchor="w"
    )
    time_label.pack(fill="x", pady=(0, 10))

    count_label = tk.Label(
        stats_area, text="Nodes explored: --", font=MAIN_FONT,
        bg=WINDOW_COLOUR, justify="left", anchor="w"
    )
    count_label.pack(fill="x", pady=(0, 18))

    comparison_title = tk.Label(
        stats_area, text="Solver comparison",
        font=("Times New Roman", 12, "bold"),
        fg=HEADING_COLOUR, bg=WINDOW_COLOUR, anchor="w"
    )
    comparison_title.pack(fill="x", pady=(0, 6))

    compare_label = tk.Label(
        stats_area, text="Comparison: run both solvers",
        font=("Times New Roman", 11), bg=WINDOW_COLOUR,
        wraplength=350, justify="left", anchor="nw"
    )
    compare_label.pack(fill="x", anchor="w")

    # CENTER: The file name and puzzle board.
    center_area = tk.Frame(page_area, bg=WINDOW_COLOUR)
    center_area.grid(row=0, column=1, sticky="n", pady=(4, 0))

    file_info = tk.Label(
        center_area, text="No puzzle loaded", font=MAIN_FONT,
        bg=WINDOW_COLOUR, fg=HEADING_COLOUR
    )
    file_info.pack(pady=(5, 10))

    puzzle_area = tk.Frame(center_area, bg=WINDOW_COLOUR)
    puzzle_area.pack()

    # RIGHT: Only three buttons, shown vertically.
    buttons_area = tk.LabelFrame(
        page_area, text="Controls", font=("Times New Roman", 14, "bold"),
        fg=HEADING_COLOUR, bg=WINDOW_COLOUR, padx=12, pady=14
    )
    buttons_area.grid(row=0, column=2, sticky="nsew", padx=(12, 0))

    file_button = tk.Button(
        buttons_area, text="Load TXT Puzzle", font=MAIN_FONT,
        width=16, padx=4, pady=7
    )
    file_button.pack(pady=(6, 14))

    back_button = tk.Button(
        buttons_area, text="Backtracking", font=MAIN_FONT,
        width=16, padx=4, pady=7, state="disabled"
    )
    back_button.pack(pady=(0, 14))

    ac_button = tk.Button(
        buttons_area, text="AC3", font=MAIN_FONT,
        width=16, padx=4, pady=7, state="disabled"
    )
    ac_button.pack()

    # Keep the exact same return order expected by Futoshiki.py.
    return (main_window, puzzle_area, file_info, message_label,
            file_button, back_button, ac_button, time_label,
            count_label, compare_label)


def create_grid(puzzle_area, board_size):
    """Clear the previous grid, then draw new boxes using the TXT size."""
    if not 2 <= board_size <= 9:
        raise ValueError("The grid size must be between 2 and 9.")

    for old_item in puzzle_area.winfo_children():
        old_item.destroy()

    def check_input(typed_text):
        return typed_text == "" or (len(typed_text) == 1 and
                                     typed_text in "123456789"[:board_size])

    input_check = puzzle_area.register(check_input)
    board_boxes = []

    for row_num in range(board_size):
        one_line = []
        for col_num in range(board_size):
            one_box = tk.Entry(
                puzzle_area, width=2, justify="center",
                font=("Times New Roman", 20 if board_size <= 6 else 15),
                relief="solid", bd=1, validate="key",
                validatecommand=(input_check, "%P")
            )
            space = 6 if board_size <= 6 else 3
            one_box.grid(row=row_num * 2, column=col_num * 2,
                         padx=space, pady=space, ipady=3)
            one_line.append(one_box)
        board_boxes.append(one_line)

    return board_boxes
