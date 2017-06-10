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

def find_twins(values, box_pairs):
    """Determine all the naked twins that exist on the Sudoku.
    
    Input: Sudoku in dictionary form and all boxes with length of two.
    Output: Resulting naked twins dictionary.
    """
    naked_twins = dict()
    for twin_box in box_pairs:
        boxes = peers[twin_box]
        pairs = box_pairs & boxes
        # Define a dictionary to determine if there are pairs with same value in the
        # same unit. The key of the dictionary is the numeric value of a box and the
        # dictionary value will be a list of the boxes. Such as {'27':['H1', 'A1']}.
        value_boxes = dict()
        value_boxes[values[twin_box]] = list()
        value_boxes[values[twin_box]].append(twin_box)
        for box in pairs:
            value = values[box]
            if value not in value_boxes:
                value_boxes[value] = list()
                value_boxes[value].append(box)
            else:
                value_boxes[value].append(box)
        # From the dictionary built above determine if there are naked twins.
        # The key of the dictionary will be a pair of boxes sorted such as "A1H1"
        # and the value will be a sorted list of such boxes like (['A1', 'H1']).
        for value in value_boxes:
            if len(value_boxes[value]) == 2:
                pairs = sorted(value_boxes[value])
                size_diag_one = len(diag_one & set(pairs))
                size_diag_two = len(diag_two & set(pairs))
                key = pairs[0] + pairs[1]
                # This rule determine if are naked pairs if two boxes belongs to the same row, column or diagonal.
                if key not in naked_twins and (pairs[0][0] == pairs[1][0] or pairs[0][1] == pairs[1][1]
                                               or size_diag_one == 2 or size_diag_two == 2):
                    naked_twins[key] = pairs
    return naked_twins

def eliminate_digits(values, digits, boxes):
    """Eliminate all the provided digits from the provided boxes.

    Input: Sudoku in dictionary form, digits that will be replaced on the given boxes.
    """
    for box in boxes:
        for digit in digits:
            values[box] = values[box].replace(digit, '')
            assign_value(values, boxes, values[box])

def eliminate_twins_units(values, twin_boxes):
    """Eliminate all the naked twins on Sudoku.

    Input: Sudoku in dictionary form and the naked twins that need to be eliminated in the Sudoku.
    Output: Resulting Sudoku in dictionary form after eliminating naked twins.
    """
    for key in twin_boxes:
        # Extract the pair of naked twins that will be used
        twins = twin_boxes[key]
        box_one = twins[0]
        box_two = twins[1]
        # Determine the boxes that needs to be updated
        boxes_1 = peers[box_one]
        boxes_2 = peers[box_two]
        all_boxes = boxes_1 & boxes_2
        # Update boxes with length greater than one
        boxes = [box for box in all_boxes if len(values[box]) > 1]
        digits = values[box_one]
        eliminate_digits(values, digits, boxes)
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    pair_boxes = list()
    # Find all the boxes with length of two
    for box in boxes:
        if len(values[box]) == 2:
            pair_boxes.append(box)
    # Remove all the duplicate boxes
    pair_boxes = set(pair_boxes)
    # Determine the proper naked twins
    naked_twins = find_twins(values, pair_boxes)
    # Eliminate all the naked twins from the Sudoku
    eliminate_twins_units(values, naked_twins)
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
