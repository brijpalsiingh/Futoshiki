import random
from pathlib import Path

TEST_FOLDER = Path(__file__).resolve().parent / "test_puzzles"


def make_pair(size, seed, easy_fixed, easy_arrows, hard_fixed, hard_arrows):
    random_maker = random.Random(seed)
    digits = list(range(1, size + 1))
    random_maker.shuffle(digits)
    move_rows = random_maker.randrange(size)
    move_cols = random_maker.randrange(size)

    solution = [
        [digits[(row + move_rows + col + move_cols) % size]
         for col in range(size)]
        for row in range(size)
    ]

    cells = [(row, col) for row in range(size) for col in range(size)]
    random_maker.shuffle(cells)

    adjacencies = (
        [((row, col), (row, col + 1))
         for row in range(size) for col in range(size - 1)]
        + [((row, col), (row + 1, col))
           for row in range(size - 1) for col in range(size)]
    )
    random_maker.shuffle(adjacencies)

    for level, given_count, arrow_count in [
        ("easy", easy_fixed, easy_arrows),
        ("hard", hard_fixed, hard_arrows),
    ]:
        lines = [
            f"# {level.title()} {size}x{size}; generated reproducibly with seed {seed}",
            "SIZE", str(size), "", "GIVENS",
        ]
        for row, col in sorted(cells[:given_count]):
            lines.append(f"{row+1},{col+1},{solution[row][col]}")

        lines.extend(["", "INEQUALITIES"])
        for first, second in sorted(adjacencies[:arrow_count]):
            row, col = first
            row2, col2 = second
            sign = "<" if solution[row][col] < solution[row2][col2] else ">"
            lines.append(f"{row+1},{col+1},{sign},{row2+1},{col2+1}")

        target = TEST_FOLDER / f"{level}_{size}x{size}.txt"
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Created {target.name}: {given_count} givens, {arrow_count} inequalities")


def main():
    TEST_FOLDER.mkdir(exist_ok=True)
    # Easy uses a superset of the givens and inequalities used in Hard,
    # so both levels are based on the same hidden valid solution.
    make_pair(4, 161, 9, 10, 2, 3)
    make_pair(6, 161, 20, 29, 7, 12)
    make_pair(8, 122, 40, 70, 26, 50)

    (TEST_FOLDER / "unsolvable_4x4.txt").write_text(
        "# Impossible cycle A<B<C<D<A; valid syntax, no mathematical solution\n"
        "SIZE\n4\nGIVENS\nINEQUALITIES\n"
        "1,1,<,1,2\n1,2,<,2,2\n2,2,<,2,1\n2,1,<,1,1\n",
        encoding="utf-8",
    )
    (TEST_FOLDER / "malformed_input.txt").write_text(
        "# 9 is outside the valid SIZE 4 domain\n"
        "SIZE\n4\nGIVENS\n1,1,9\nINEQUALITIES\n",
        encoding="utf-8",
    )
    print("Created unsolvable_4x4.txt and malformed_input.txt")


if __name__ == "__main__":
    main()
