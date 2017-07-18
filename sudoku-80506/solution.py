assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(a, b):
    "Cross product of elements in A and elements in B."
    return [s+t for s in a for t in b]

def diagonals(rows,columns):
    "returns a list of the two diagonal units"
    assert len(rows) == len(cols)
    #get the diagonal, starting with the top left corner
    first_diagonal = [rows[i]+columns[i] for i in range(len(rows))]
    #reverse the row string
    reversed_row_string = rows[::-1]
    #get the second diagonal, starting with the top right corner
    second_diagonal = [reversed_row_string[i]+columns[i] for i in range(len(reversed_row_string))]
    #return a list of the first and second diagonals
    return [first_diagonal, second_diagonal]

boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diagonal_units = diagonals(rows,cols)
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

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

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Find all instances of naked twins	
    # Eliminate the naked twins as possibilities for their peers	
    #get all possible twins - boxes that only have two values
    possible_twins = [box for box in values if len(values[box]) == 2]
    for possible_twin in possible_twins:   
           #for each possible twin, check each unit of the box for a twin
           for unit in units[possible_twin]:
               #find all instances of the twins - they will have the same values
               twins = [box for box in unit if values[box] == values[possible_twin] and box != possible_twin]                            
               if (len(twins) > 0):
                   #if there are twins, update the non-twins of the unit accordingly
                   non_twins = [box for box in unit if values[box] != values[possible_twin] and box != possible_twin]
                   for box in non_twins:
                   #eliminate the naked twins as possibilites from peers
                       for twin_value in values[possible_twin]:
                           values = assign_value(values, box, values[box].replace(twin_value, ''))
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
    assert len(grid) == 81
    grid_dict = dict(zip(boxes, grid))
    for item in grid_dict:
        if  grid_dict[item] == '.':
            grid_dict[item] = '123456789'
    return grid_dict 

def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
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
    #loop through all boxes
    for box in values:
        #if box contains single value
        if len(values[box]) == 1:
            #loop through peers
            for peer in peers[box]:
                #remove the value from peer
                values[peer] = values[peer].replace(values[box],"")
    return values  

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    #loop through square units
    for unit in unitlist:
        #loop through all possible values
        for value in '123456789':
            #find occurrences of that value in the unit
            occurences_of_value = [box for box in unit if value in values[box]]
            #if only one occurrence of that value
            if len(occurences_of_value) == 1:
                #set the value of that box accordingly
                values[occurences_of_value[0]] = value
    return values

def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Your code here: Use the Eliminate Strategy
        eliminate(values)
        # Your code here: Use the Only Choice Strategy
        only_choice(values)
        # Apply Naked Twins Strategy
        naked_twins(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)  
    if values is False:
        return False
    #if puzzle is solved, return the solved puzzle
    if all(len(values[box]) == 1 for box in boxes): 
        return values 
    # Choose one of the unfilled squares with the fewest possibilities
    a,box = min((len(values[box]), box) for box in boxes if len(values[box]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[box]:
        attempted_sudoku = values.copy()
        attempted_sudoku[box] = value
        #recursively call the search function on attempted Sudoku
        attempt = search(attempted_sudoku)
        #if the attempt is successful, return the solution
        if attempt:
            return attempt
        
def solve(grid):
    values = grid_values(grid)
    attempt = search(values)
    return attempt

if __name__ == '__main__':
    #diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    diag_sudoku_grid = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'   
    attempt = solve(diag_sudoku_grid)
    display(attempt)
    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)
    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
