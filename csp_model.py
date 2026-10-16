class FutoshikiCSP:
    def __init__(self, game_data):
        self.size = game_data["size"]
        self.givens = dict(game_data["givens"])
        board_size = self.size

        # A box is identified by its (row, column) position.
        self.variables = [(row_num, col_num)
                          for row_num in range(board_size)
                          for col_num in range(board_size)]
        self.domains = {}
        for place in self.variables:
            if place in self.givens:
                self.domains[place] = {self.givens[place]}
            else:
                self.domains[place] = set(range(1, board_size + 1))

        # Every box must differ from boxes in the same row and column.
        self.peers = {}
        for row_num, col_num in self.variables:
            row_boxes = {(row_num, other_col) for other_col in range(board_size)
                         if other_col != col_num}
            col_boxes = {(other_row, col_num) for other_row in range(board_size)
                         if other_row != row_num}
            self.peers[(row_num, col_num)] = row_boxes | col_boxes

        self.inequality_neighbors = {place: [] for place in self.variables}
        self.inequalities = []

        for (row_num, col_num), sign in game_data["horizontal_clues"].items():
            if sign not in ("<", ">"):
                raise ValueError("Horizontal comparison must be < or >")
            self._add_inequality((row_num, col_num), sign, (row_num, col_num + 1))

        for (row_num, col_num), sign in game_data["vertical_clues"].items():
            if sign not in ("∧", "∨"):
                raise ValueError("Vertical comparison must be ∧ or ∨")
            comparison = "<" if sign == "∧" else ">"
            self._add_inequality((row_num, col_num), comparison,
                                 (row_num + 1, col_num))

        self.neighbors = {place: set(self.peers[place]) for place in self.variables}
        self.relations = {}
        for place in self.variables:
            for other_place, comparison in self.inequality_neighbors[place]:
                self.relations[(place, other_place)] = comparison

    def _add_inequality(self, first_place, comparison, second_place):
        if first_place not in self.domains or second_place not in self.domains:
            raise ValueError("A comparison is outside the puzzle")
        self.inequalities.append((first_place, comparison, second_place))
        self.inequality_neighbors[first_place].append((second_place, comparison))
        backwards = ">" if comparison == "<" else "<"
        self.inequality_neighbors[second_place].append((first_place, backwards))

    def values_compatible(self, first_place, first_number,
                          second_place, second_number):
        if second_place not in self.neighbors[first_place]:
            return True
        if first_number == second_number:
            return False
        comparison = self.relations.get((first_place, second_place))
        if comparison == "<":
            return first_number < second_number
        if comparison == ">":
            return first_number > second_number
        return True

    def is_consistent(self, place, try_number, filled_boxes):
        if place not in self.domains or try_number not in self.domains[place]:
            return False
        for other_place in self.peers[place]:
            if filled_boxes.get(other_place) == try_number:
                return False
        for other_place, comparison in self.inequality_neighbors[place]:
            other_number = filled_boxes.get(other_place)
            if other_number is None:
                continue
            if comparison == "<" and try_number >= other_number:
                return False
            if comparison == ">" and try_number <= other_number:
                return False
        return True

    def givens_are_consistent(self):
        for place, fixed_number in self.givens.items():
            other_givens = {other_place: other_number
                            for other_place, other_number in self.givens.items()
                            if other_place != place}
            if not self.is_consistent(place, fixed_number, other_givens):
                return False
        return True

    def is_solution(self, filled_boxes):
        if set(filled_boxes) != set(self.variables):
            return False
        for place, try_number in filled_boxes.items():
            other_boxes = {other_place: other_number
                           for other_place, other_number in filled_boxes.items()
                           if other_place != place}
            if not self.is_consistent(place, try_number, other_boxes):
                return False
        return True
