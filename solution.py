# Sudoku AI

def cross(a, b):
    return [s + t for s in a for t in b]

def diag_peers(peers):
    for diagonal in diagonals:
        for box in diagonal:
            peers[box].update(diagonal)
            peers[box].remove(box)
    return peers

assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
diag_one = set(rows[c] + str(c + 1) for c in (0, 1, 2, 3, 4, 5, 6, 7, 8))
diag_two = set(rows[c] + str(9 - c) for c in (0, 1, 2, 3, 4, 5, 6, 7, 8))
diagonals = [diag_one, diag_two]
unitlist = row_units + column_units + square_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)
peers = diag_peers(peers)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def grid_values(grid):
    """Convert grid string into {<box>: <value>} dict with '123456789' value for empties.

    Args:
        grid: Sudoku grid in string form, 81 characters long
    Returns:
        Sudoku grid in dictionary form:
        - keys: Box labels, e.g. 'A1'
        - values: Value in corresponding box, e.g. '8', or '123456789' if it is empty.
    """
    values = []
    all_digits = '123456789'
    for c in grid:
        if c == '.':
            values.append(all_digits)
        elif c in all_digits:
            values.append(c)
    assert len(values) == 81
    return dict(zip(boxes, values))

def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit, '')
    return values

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values

def find_twins(values, pair_boxes, array):
    pairs = list()
    for row in array:
        new_boxes = pair_boxes & set(row)
        row_pairs = dict()
        if len(new_boxes) > 1:
            for box in new_boxes:
                key = values[box]
                if key not in row_pairs:
                    row_pairs[key] = list()
                row_pairs[key].append(box)
            pairs.append(row_pairs)
    naked_twins = list()
    for row_pairs in pairs:
        for key in row_pairs:
            if len(row_pairs[key]) == 2:
                tmp = dict()
                tmp[key] = list(row_pairs[key])
                naked_twins.append(tmp)
    return naked_twins

def eliminate_twins(values, naked_twins, array, index):
    alpha = False
    if index == 0:
        alpha = True
    for twins in naked_twins:
        for key in twins:
            digits = key
            boxes = twins[key]
            row = boxes[0][index]
            if alpha:
                row = rows.index(row)
            else:
                row = int(row) - 1
            boxes = set(array[row]) - set(boxes)
            for box in boxes:
                if len(values[box]) > 1:
                    for digit in digits:
                        values[box] = values[box].replace(digit, '')
    return values


def find_diagonal_twins(values, pair_boxes, diagonal):
    new_boxes = pair_boxes & diagonal
    diagonal_pairs = dict()
    for box in new_boxes:
        key = values[box]
        if key not in diagonal_pairs:
            diagonal_pairs[key] = list()
        diagonal_pairs[key].append(box)
    twin_diagonal = dict()
    for key in diagonal_pairs:
        if len(diagonal_pairs[key]) == 2:
            twin_diagonal[key] = diagonal_pairs[key]
    return twin_diagonal

def eliminate_diagonal_twins(values, twin_diagonal, diagonal):
    for key in twin_diagonal:
        digits = key
        twin_boxes = set(twin_diagonal[key])
        boxes = diagonal - twin_boxes
        for box in boxes:
            if len(values[box]) > 1:
                for digit in digits:
                    values[box] = values[box].replace(digit, '')
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    display(values)
    # Define a dictionary per row and col with boxes of length two
    pair_boxes = list()
    for box in boxes:
        if len(values[box]) == 2:
            pair_boxes.append(box)
    pair_boxes = set(pair_boxes)
    print(pair_boxes)
    # Determine if there are naked twins per row and per col
    naked_rows = find_twins(values, pair_boxes, row_units)
    naked_cols = find_twins(values, pair_boxes, column_units)
    naked_dia_one = find_diagonal_twins(values, pair_boxes, diag_one)
    naked_dia_two = find_diagonal_twins(values, pair_boxes, diag_two)
    # Eliminate the naked twins as possibilities for their peers rows
    values = eliminate_twins(values, naked_rows, row_units, 0)
    values = eliminate_twins(values, naked_cols, column_units, 1)
    values = eliminate_diagonal_twins(values, naked_dia_one, diag_one)
    values = eliminate_diagonal_twins(values, naked_dia_two, diag_two)
    print("\n")
    display(values)
    return values

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, try all possible values."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False  ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values  ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        assign_value(values, s, value)
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments

        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
