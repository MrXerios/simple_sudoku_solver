from copy import copy
from collections import defaultdict
from itertools import product

# Structure of a grid
_list_rows = [frozenset(9*row + col for col in range(9)) for row in range(9)]
_list_cols = [frozenset(9*row + col for row in range(9)) for col in range(9)]
_list_boxes = [frozenset((box // 3) * 27 + (box % 3) * 3 + 9 * (i // 3) + (i % 3) for i in range(9)) for box in range(9)]
_list_houses = _list_rows + _list_cols + _list_boxes

# Create dict of row / col / box a slot belongs to.
_row = dict()
for r in _list_rows:
    for slot in r:
        _row[slot] = r

_col = dict()
for c in _list_cols:
    for slot in c:
        _col[slot] = c

_box = dict()
for b in _list_boxes:
    for slot in b:
        _box[slot] = b

# Create dict of the houses of each slot
_houses = {slot:(_row[slot], _col[slot], _box[slot]) for slot in range(81)}

# Create dict of neighbours of a slot
_neighbours = {slot: (_row[slot] | _col[slot] | _box[slot]) - {slot} for slot in range(81)}

# util functions
def index_rows(slots): return {slot // 9 for slot in slots}
def index_cols(slots): return {slot % 9 for slot in slots}
def index_boxes(slots): return {3 * (slot //9 // 3) + (slot % 9 // 3) for slot in slots}

def same_row(slots): return len(index_rows(slots)) == 1
def same_col(slots): return len(index_cols(slots)) == 1
def same_box(slots): return len(index_boxes(slots)) == 1

_strategies = set()
def strategy(f=None, repeat=False):
    if f is not None:
        _strategies.add((f, repeat))
        return f
    else:
        return lambda f: strategy(f, repeat=repeat)



class Grid:

    # lists of all houses of the Grid
    list_rows = _list_rows
    list_cols = _list_cols
    list_boxes = _list_boxes
    list_houses = _list_houses

    # Access houses from slot
    row, col, box = _row, _col, _box
    houses = _houses

    # Neighbours of a slot
    neighbours = _neighbours

    # Solving strategies
    strategies = _strategies

    def __init__(self, possible_slots: str):

        # Create dict of bool to know if a given slot if fixed in init
        self.isInit = {
            slot: val.isdigit() for slot, val in enumerate(possible_slots)
        }

        # Create dict of possible values for each slot
        self.possible_values = {
            slot: {int(val)} if val.isdigit() else {1, 2, 3, 4, 5, 6, 7, 8, 9}
            for slot, val in enumerate(possible_slots)
        }

        # Create dict of possible slots for each value
        self.possible_slots = dict()
        for val in {1, 2, 3, 4, 5, 6, 7, 8, 9}:
            self.possible_slots[val] = set(range(81))

        # Create solution dict
        self.solution = defaultdict(lambda: None)

        # Clean up possible_values
        for slot, val in enumerate(possible_slots):
            if val.isdigit():
                self.fix(slot, int(val))

    def __str__(self):
        values = [self.solution[slot] for slot in range(81)]
        values_str = "".join(['x' if not val else str(val) for val in values])
        rows = [" | ".join([values_str[3*col + 9*row:3*col+3 + 9*row] for col in range(3)]) for row in range(9)]
        grid = "\n----+-----+----\n".join(["\n".join(rows[i*3:i*3+3]) for i in range(3)])
        return grid

    def __repr__(self):
        return str(self)

    @property
    def isSolved(self):
        for slot in range(81):
            if self.solution[slot] is None:
                return False
        return True

    @property
    def contradiction(self):
        for slot in range(81):
            if self.solution[slot] is None and self.possible_values[slot] == set():
                return True
        return False

    def remove(self, slots, vals):
        for slot in slots:
            self.possible_values[slot] -= vals

        for val in vals:
            self.possible_slots[val] -= slots

    def fix(self, slot, val):

        # Fix slot
        self.solution[slot] = val
        self.possible_values[slot] -= {val}
        self.possible_slots[val] -= {slot}

        # There cannot be val in the neighbours of slot:
        self.remove(self.neighbours[slot], {val})

        # slot cannot contain another val:
        self.remove({slot}, {1, 2, 3, 4, 5, 6, 7, 8, 9} - {val})

    @strategy(repeat=True)
    def fix_naked_singles(self):
        """Find and fix slots that can only contain one single value"""
        changed = False
        for slot, vals in self.possible_values.items():
            # If only one possibility for slot and slot isn't fixed yet
            if len(self.possible_values[slot]) == 1:
                change = True
                self.fix(slot, copy(self.possible_values[slot]).pop())

        return changed

    @strategy(repeat=True)
    def fix_hidden_singles(self):
        """Find and fix values that can only be in one single slot in
        a house"""
        changed = False
        for house in self.list_houses:
            for val in range(1, 10):
                possible_slots_in_house = self.possible_slots[val] & house
                if len(possible_slots_in_house) == 1:
                    changed = True
                    self.fix(copy(possible_slots_in_house).pop(), val)
        return changed

    @strategy
    def isolate_naked_tuples(self):
        """Find and isolate tuples (pairs and triples most of the time)
        of slots that can only contain a tuple (pairs and triples...)
        of values"""
        for house in self.list_houses:
            n_map = defaultdict(set)
            for slot in house:
                if len(self.possible_values[slot]) >= 2:
                    possible_values_key = frozenset(self.possible_values[slot])
                    for key, slots in copy(n_map).items():
                        n_map[possible_values_key | key] = slots | {slot}
                    n_map[possible_values_key] |= {slot}

            for tuple_values, tuple_slots in n_map.items():
                if len(tuple_values) == len(tuple_slots):
                    # naked tuple found
                    self.remove(house - tuple_slots, tuple_values)

    @strategy
    def isolate_hidden_tuples(self):
        for house in self.list_houses:
            n_map = defaultdict(set)
            for val in range(1, 10):
                possible_slots_in_house = self.possible_slots[val] & house
                if len(possible_slots_in_house) >= 2:
                    possible_slots_key = frozenset(possible_slots_in_house)
                    for key, vals in copy(n_map).items():
                        n_map[possible_slots_key | key] = vals | {val}
                    n_map[possible_slots_key] |= {val}

            for tuple_slots, tuple_vals in n_map.items():
                if len(tuple_slots) == len(tuple_vals):
                    # hidden tuple found
                    self.remove(tuple_slots, {1, 2, 3, 4, 5, 6, 7, 8, 9} - tuple_vals)

    @strategy
    def pointing_tuples(self):
        for val in {1, 2, 3, 4, 5, 6, 7, 8, 9}:
            for box in self.list_boxes:
                s_in_box = self.possible_slots[val] & box
                if same_row(s_in_box) or same_col(s_in_box):
                    rc = (
                        self.list_rows[index_rows(s_in_box).pop()]
                        if same_row(s_in_box)
                        else self.list_cols[index_cols(s_in_box).pop()]
                    )
                    self.remove(rc - box, {val})

    @strategy
    def x_wing(self):
        for val in {1, 2, 3, 4, 5, 6, 7, 8, 9}:
            for dir, other_dir, index_func in (
                (self.list_rows, self.list_cols, index_cols),
                (self.list_cols, self.list_rows, index_rows),
            ):
                for i_line1, line1 in enumerate(dir):
                    for line2 in dir[i_line1 + 1:]:
                        slots_1 = self.possible_slots[val] & line1
                        slots_2 = self.possible_slots[val] & line2

                        if len(slots_1) == 2 and len(slots_2) == 2:
                            i_line2 = index_func(slots_1 | slots_2)
                            if len(i_line2) == 2:
                                # X-wing found
                                # Remove all other instances of val from
                                # found lines in other direction
                                for other_line in {other_dir[i] for i in i_line2}:
                                    self.remove(other_line - (slots_1 | slots_2), {val})

    @strategy
    def y_wing(self):
        for slot in range(81):
            p_vals = self.possible_values[slot]
            row_y = set()
            for n in self.row[slot] - {slot}:
                if len(self.possible_values[n]) == 2:
                    if len(self.possible_values[n] & p_vals) == 2:
                        row_y |= {n}
            col_y = set()
            for n in self.col[slot] - {slot}:
                if len(self.possible_values[n]) == 2:
                    if len(self.possible_values[n] & p_vals) == 2:
                        col_y |= {n}

            for slot_r, slot_c in product(row_y, col_y):
                val_r = self.possible_values[slot_r]
                val_c = self.possible_values[slot_c]
                if val_r & val_c:
                    self.remove(
                        self.col[slot_r] & self.row[slot_c],
                        val_r & val_c
                    )

    def run_strategies(self):
        for strat, repeat in self.strategies:
            if repeat:
                while strat(self): pass
            else:
                strat(self)

    def solve(self, max_iter=100):
        iter = 0
        while not self.isSolved and iter < max_iter:
            self.run_strategies()
            iter += 1
        return self

if __name__ == "__main__":

    sudoku = '1' + 'x'*80

    # sudoku = "XX9XX87XX2X7XXXX3XXXXXXX2XXXXX279XXXXXXX8X1X3XXXX3XXX6X8X9XXXXX3XXXX5XXXX1XXXXX54"

    # sudoku = "XXXXXX634XXXX91X8XXXXXX2X1X1XXXXXXX7XX8XXX4XXXX97X5XXXXXXX6XXXXX4XX3XXX863X1XXXXX"

    sudoku = "5XX9X6XXXXXX24XXX11XXXXXXX78XXXX21X3X36XXXX9X7XXXXXXXXXX1X3X86XXXXXXX3XXXX37XXXX9"

    # sudoku = "XXX2XX5X9XXX5XXXXX295478XXX15X3X4X9XXX6XXXX5XX74X5X2XXXXXX23X4XX6384XXXX4X8XXX73X"

    # sudoku = "81X56X2XXXXXX7XXX3XX6XXXXXX96XX5XX7XXX4XXX9XXXX26XXXXX59X1XX8XXXXXXX8X2X4XXXXXXXX"

    g = Grid(sudoku)
    print(g, "\n")

    g.solve()

    print(g)

