from pathlib import Path
from tkinter import filedialog, messagebox
from queue import Queue, Empty
from threading import Thread

from gui import create_gui, create_grid
from game_inputfile import display_game_input
from puzzle_loader import load_puzzle, PuzzleFileError
from backtracking import solve_backtracking, DEFAULT_TIMEOUT_SECONDS
from ac3_solver import solve_ac3
from validator import validate_solver_result


def main():
    (main_window, puzzle_area, file_info, message_label,
     file_button, back_button, ac_button, time_label,
     count_label, compare_label) = create_gui()

    loaded_game = None
    board_boxes = None
    busy_solving = False
    answer_queue = Queue()
    old_results = {}

    def show_comparison():
        show_lines = ["Comparison of the two solvers:"]
        for method_name in ("Backtracking", "AC3"):
            saved_answer = old_results.get(method_name)
            if saved_answer is None:
                show_lines.append(method_name + ": not run")
            else:
                show_lines.append(
                    f"{method_name}: {saved_answer.status}, "
                    f"{saved_answer.runtime_seconds:.6f} seconds, "
                    f"{saved_answer.nodes_explored} nodes"
                )
        compare_label.config(text="\n".join(show_lines))

    def show_numbers(answer_board=None):
        # Each new solver run starts with the original given numbers.
        if loaded_game is None or board_boxes is None:
            return
        board_size = loaded_game["size"]
        for row_num in range(board_size):
            for col_num in range(board_size):
                one_box = board_boxes[row_num][col_num]
                one_box.config(state="normal", bg="white")
                one_box.delete(0, "end")
                place = (row_num, col_num)
                if place in loaded_game["givens"]:
                    one_box.insert(0, str(loaded_game["givens"][place]))
                    one_box.config(state="readonly", readonlybackground="#DCEBFA")
                elif answer_board is not None:
                    one_box.insert(0, str(answer_board[row_num][col_num]))
                    one_box.config(state="readonly", readonlybackground="#E5F3E7")

    def load_game_file():
        nonlocal loaded_game, board_boxes
        if busy_solving:
            return

        chosen_file = filedialog.askopenfilename(
            parent=main_window, title="Choose a Futoshiki TXT file",
            filetypes=[("TXT files", "*.txt"), ("All files", "*.*")]
        )
        if not chosen_file:
            return

        try:
            new_game = load_puzzle(chosen_file)
        except PuzzleFileError as file_problem:
            messagebox.showerror("Invalid TXT File",
                                 f"File: {Path(chosen_file).name}\n\n{file_problem}",
                                 parent=main_window)
            message_label.config(text="Status: Invalid puzzle - old puzzle kept")
            return

        # Make the new board only after the file has passed validation.
        new_boxes = create_grid(puzzle_area, new_game["size"])
        display_game_input(puzzle_area, new_boxes, new_game)
        board_boxes = new_boxes
        loaded_game = new_game
        file_info.config(text=f"Grid: {new_game['size']} x {new_game['size']} "
                              f"| File: {Path(chosen_file).name}")
        message_label.config(text="Status: Puzzle loaded")
        time_label.config(text="Runtime: --")
        count_label.config(text="Nodes explored: --")
        back_button.config(state="normal")
        ac_button.config(state="normal")
        old_results.clear()
        show_comparison()

    def start_solving(method_name):
        nonlocal busy_solving
        if loaded_game is None or busy_solving:
            return
        busy_solving = True
        show_numbers()
        file_button.config(state="disabled")
        back_button.config(state="disabled")
        ac_button.config(state="disabled")
        message_label.config(text=f"Status: Solving with {method_name}...")
        time_label.config(text="Runtime: --")
        count_label.config(text="Nodes explored: --")

        game_copy = {
            "size": loaded_game["size"],
            "givens": dict(loaded_game["givens"]),
            "horizontal_clues": dict(loaded_game["horizontal_clues"]),
            "vertical_clues": dict(loaded_game["vertical_clues"]),
        }

        def calculate_answer():
            try:
                if method_name == "Backtracking":
                    solve_answer = solve_backtracking(game_copy, timeout_seconds=DEFAULT_TIMEOUT_SECONDS)
                else:
                    solve_answer = solve_ac3(game_copy, timeout_seconds=DEFAULT_TIMEOUT_SECONDS)
                answer_queue.put((method_name, solve_answer, None))
            except Exception as problem:
                answer_queue.put((method_name, None, problem))

        # Do not freeze Tkinter while the search works.
        Thread(target=calculate_answer, daemon=True).start()
        main_window.after(50, get_answer)

    def get_answer():
        nonlocal busy_solving
        try:
            method_name, solve_answer, problem = answer_queue.get_nowait()
        except Empty:
            main_window.after(50, get_answer)
            return

        busy_solving = False
        file_button.config(state="normal")
        back_button.config(state="normal")
        ac_button.config(state="normal")

        if problem is not None:
            message_label.config(text="Status: Solver error")
            messagebox.showerror("Solver Error", str(problem), parent=main_window)
            return

        passed, reasons = validate_solver_result(loaded_game, solve_answer)
        if not passed:
            message_label.config(text="Status: Invalid solver result")
            messagebox.showerror("Solution Check Failed", "\n".join(reasons),
                                 parent=main_window)
            return

        # Task 4: also print results to the Spyder/Python console.
        print(f"{method_name}: {solve_answer.status} | "
              f"Runtime: {solve_answer.runtime_seconds:.6f} seconds | "
              f"Nodes visited: {solve_answer.nodes_explored}")

        old_results[method_name] = solve_answer
        time_label.config(text=f"Runtime: {solve_answer.runtime_seconds:.6f} s")
        count_label.config(text=f"Nodes explored: {solve_answer.nodes_explored}")
        show_comparison()
        if solve_answer.status == "Solved":
            show_numbers(solve_answer.grid)
        message_label.config(text=f"Status: {solve_answer.status} ({method_name})")

    file_button.config(command=load_game_file)
    back_button.config(command=lambda: start_solving("Backtracking"))
    ac_button.config(command=lambda: start_solving("AC3"))
    show_comparison()
    main_window.mainloop()


if __name__ == "__main__":
    main()
