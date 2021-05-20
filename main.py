import os
import typing
import webbrowser
from svgwrite import shapes, Drawing
from copy import deepcopy

# Typing
StrVector = typing.List[str]
IntVector = typing.List[int]
StringMatrix = typing.List[StrVector]
NumberMatrix = typing.List[IntVector]
CoordinateVector = typing.List[tuple]

# Map the strings
BLOCK = '#'
EXIT = 'E'
START = '^'
SPACE = ' '

MENU_TEXT = """\n** Main menu **

Available actions
0 = exit
1 = Look up for maps from default location {location} and select and run all (exits at the end).
2 = Look up for maps from default location (from: {location})
3 = Look up for maps from specific location 
"""
FILE_SELECTION_TEXT = """Please select a text file to run

0 = select all
{files}
"""
INPUT_FOLDER_TEXT = """Input folder path
"""

DEFAULT_PATH = os.path.join(os.getcwd(), 'maps')
TEST_STEPS = [20, 150, 200]
MAZE_WALL_SIZE = 20


def main():
    """ Main program loop """
    print('Welcome to use maze solver!')
    while True:
        user_input = with_int_parsed_input(MENU_TEXT.format(location=DEFAULT_PATH))
        if user_input == -1:
            # Invalid input
            continue
        if user_input == 0:
            print('Exiting...')
            break
        if user_input == 1:
            files = get_files()
            analyse_input(files, DEFAULT_PATH)
            print('Done! Exiting...')
            break
        elif user_input == 2:
            file_selection_logic()
        elif user_input == 3:
            user_path = input(INPUT_FOLDER_TEXT)
            if not os.path.isdir(user_path):
                print('{} is not a valid path. Please input valid directory path'.format(user_path))
                continue
            else:
                file_selection_logic(user_path)
        else:
            print('No option for {}'.format(user_input))


def file_selection_logic(path: str = None):
    """ File selection logic from folder structure to maze analysis """
    if path is None:
        path = DEFAULT_PATH
    files = get_files(path)
    if len(files) > 0:
        # Parse user input and offer file options as text
        selected_file = with_int_parsed_input(FILE_SELECTION_TEXT.format(
            files='\n'.join((['{} = {}'.format(i + 1, file) for i, file in enumerate(files)]))))
        if selected_file == -1:
            print('Invalid input!')
            return
        if selected_file == 0:
            analyse_input(files, path)
        else:
            if selected_file - 1 < len(files):
                analyse_input([files[selected_file - 1]], path)
    else:
        print('No files found from folder!')


def analyse_input(files: list, path: str):
    """ Handles files and loops them """
    try:
        maps = [read_map(os.path.join(path, file)) for file in files]
    except Exception as e:
        print('Could not load all maps from {}. '
              'Please make sure that you only have valid text files in the folder'.format(path))
        return
    for i, matrix in enumerate(maps):
        print('\nSolving map {}\n*********'.format(files[i]))
        if matrix is None:
            print('Map {} is not a valid map!'.format(files[i]))
            continue
        for s in TEST_STEPS:
            calculated_matrix, result, moves = calculate_path(matrix, s, silent=True)
            print('Tried with {s} max steps'.format(s=s))
            if result:
                print('Solved puzzle: Exit is reachable after {} moves'.format(moves))
                matrix_with_path = backtrack_path(calculated_matrix)
                visualize_maze_path_as_svg(matrix_with_path, os.path.splitext(files[i])[0])
            else:
                print('Puzzle could not be solved in given moves ({})!'.format(s))


def visualize_maze_path_as_svg(matrix: NumberMatrix, name: str):
    print('Started visualization process')
    dwg = Drawing('maps\\{}.svg'.format(name))
    # Visualize the maze
    wall_size = MAZE_WALL_SIZE, MAZE_WALL_SIZE
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] == -1:
                square = shapes.Rect((j * MAZE_WALL_SIZE, i * MAZE_WALL_SIZE), wall_size, fill='grey')
                dwg.add(square)
            elif matrix[i][j] > 0:
                circle = shapes.Circle(
                    (j * MAZE_WALL_SIZE + MAZE_WALL_SIZE / 2, i * MAZE_WALL_SIZE + MAZE_WALL_SIZE / 2),
                    r=MAZE_WALL_SIZE / 3, fill='#FF0000')
                dwg.add(circle)
            elif matrix[i][j] == 0:
                circle = shapes.Circle(
                    (j * MAZE_WALL_SIZE + MAZE_WALL_SIZE / 2, i * MAZE_WALL_SIZE + MAZE_WALL_SIZE / 2),
                    r=MAZE_WALL_SIZE / 2, fill='#0000FF')
                dwg.add(circle)
            elif matrix[i][j] == -76:
                circle = shapes.Circle(
                    (j * MAZE_WALL_SIZE + MAZE_WALL_SIZE / 2, i * MAZE_WALL_SIZE + MAZE_WALL_SIZE / 2),
                    r=MAZE_WALL_SIZE / 2, fill='#00FF00')
                dwg.add(circle)
            elif matrix[i][j] == -77:
                square = shapes.Rect((j * MAZE_WALL_SIZE, i * MAZE_WALL_SIZE), wall_size, fill='black')
                dwg.add(square)
    dwg.save()
    print('Saved file {}.svg'.format(name))
    print('Opening file {} to your webbrowser...'.format(name))
    webbrowser.open('maps\\{}.svg'.format(name), new=2)


def backtrack_path(matrix: NumberMatrix) -> NumberMatrix:
    """
    Our mapping is as follows:
    -76 is used exit, -77 other exits
    -1 is a wall, numbers are ordered and tested paths
    Lets walk it backwards and return matrix where only single path is presented
    """
    path_matrix = deepcopy(matrix)

    # Just keep the skeleton
    for i in range(len(path_matrix)):
        for j in range(len(path_matrix[i])):
            if path_matrix[i][j] != -1 and path_matrix[i][j] != -77:
                # We have selected 0 as starting point... Not a good idea.
                if path_matrix[i][j] is not None and path_matrix[i][j] == 0:
                    path_matrix[i][j] = 0
                else:
                    path_matrix[i][j] = -2

    current_location = find_values_from_matrix(matrix, -76)[0]

    # Find maximum
    maximum = 0
    for row in matrix:
        m = max(i for i in row if i is not None)
        if m > maximum: maximum = m

    # MarkDown the exit
    path_matrix[current_location[0]][current_location[1]] = -76

    while maximum > 0:
        # We need to find previous step by going backwards
        directions = ['LEFT', 'RIGHT', 'DOWN', 'UP']
        list_of_possibilities = find_values_from_matrix(matrix, maximum)
        match = False
        for direction in directions:
            tile = move(current_location[0], current_location[1], len(matrix), len(matrix[0]), direction)
            if tile is None:
                # OB
                continue
            for possible_tile in list_of_possibilities:
                if tile == possible_tile:
                    # This is a match
                    match = True
                    break
            if match:
                # Lets map the next tile
                path_matrix[tile[0]][tile[1]] = maximum
                current_location = tile
                break
        maximum -= 1
    return path_matrix


def find_values_from_matrix(matrix: NumberMatrix, value: int) -> CoordinateVector:
    """"""
    matches = []
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] == value:
                matches.append((i, j))
    return matches


def with_int_parsed_input(prompt: str) -> int:
    """
    Handles user input and converts it to int.
    If user input cannot be converted to integer, returns -1
    """
    try:
        return int(input(prompt))
    except ValueError:
        print('Warning: Input was invalid')
        return -1
    except Exception as e:
        raise e


def print_info() -> str:
    info_string = """0 = exit
1 = look up for maps from default location (from: {def_loc})
2 = look up maps from specific location""".format(def_loc=os.path.join(os.getcwd(), 'maps'))
    return info_string


def get_files(user_path: str = None) -> list:
    files = []
    if user_path:
        maps_path = user_path
    else:
        maps_path = os.path.join(os.getcwd(), 'maps')
    try:
        for file in os.listdir(maps_path):
            if file.endswith('.txt'):
                files.append(file)
    except Exception as e:
        print(e)
    return files


def read_map(file_location: str) -> StringMatrix or None:
    """
    This function presumes that the input is valid. It will return None if errors.
    Strips line feed from inputs and orders strings per rows into matrixes (uses readline)
    :param file_location: Location to open file.
    :return: List of map rows, or None
    """
    try:
        matrix = []
        # No need to alter the file, just read it
        with open(file_location, 'r') as f:
            while True:
                file_line = f.readline()
                if not file_line:
                    break
                line = []
                file_line = file_line.replace('\n', '')
                for char in file_line:
                    if char in [SPACE, START, EXIT, BLOCK]:
                        line.append(char)
                    else:
                        print('The inputed file {} contained some value that is not allowed. '
                              'Please check your input file'.format(file_location))
                        raise ValueError()
                matrix.append(line)
        return matrix
    except Exception as e:
        return None


def calculate_path(matrix: StringMatrix, max_steps: int = 50, silent: bool = False) -> tuple:
    """ This presumes NxM matrix, so the check must be implemented elsewhere"""
    path_matrix = []

    for i, row in enumerate(matrix):
        path_row = []
        for j, cell in enumerate(row):
            if cell == BLOCK:
                # Mark wall
                path_row.append(-1)
            elif cell == START:
                path_row.append(0)
            elif cell == EXIT:
                # Mark exit
                path_row.append(-77)
            else:
                path_row.append(None)
        path_matrix.append(path_row)

    result = False
    moves = max_steps
    for i in range(0, max_steps):
        path_matrix, solved, stuck = calculate_move(path_matrix, i)
        if solved:
            result = True
            moves = i
            if not silent:
                print('Move {} found my way out!'.format(i))
            return path_matrix, result, moves
        if stuck:
            print('We are stuck. No available moves! This is a dead end. In move {}'.format(i))
            return path_matrix, result, i

    return path_matrix, result, moves


def calculate_move(matrix: NumberMatrix, move_number: int) -> tuple:
    """
    This function goes through all the moves possible in the matrix and maps them inside matrix
    Returns tuple with matrix, passed_maze, stuck
    matrix - returns the matrix with calculated step
    solved -  information if we have solved the puzzle
    stuck - are we stuck in the puzzle (no moves available)
    """
    # If we dont have available moves we can say we are stuck
    stuck = True
    # We have max four locations to check
    directions = ['LEFT', 'RIGHT', 'DOWN', 'UP']
    try:
        for i, row in enumerate(matrix):
            for j, cell in enumerate(row):
                if matrix[i][j] is None:
                    continue
                if matrix[i][j] == move_number:
                    for direction in directions:
                        loc = move(i, j, len(matrix), len(row), direction)
                        if loc:
                            if matrix[loc[0]][loc[1]] is None:
                                matrix[loc[0]][loc[1]] = move_number + 1
                                stuck = False
                            elif matrix[loc[0]][loc[1]] == -77:
                                # MarkDown our used exit
                                matrix[loc[0]][loc[1]] = -76
                                return matrix, True, stuck
    except IndexError:
        print('IndexError: Maze is probably not correctly formed!')
        return matrix, False, True
    return matrix, False, stuck


def move(x: int, y: int, width: int, height: int, direction: str = 'LEFT') -> tuple or None:
    if direction == 'LEFT':
        if x - 1 >= 0:
            return x - 1, y
    elif direction == 'RIGHT':
        if x + 1 < width:
            return x + 1, y
    elif direction == 'UP':
        if y - 1 >= 0:
            return x, y - 1
    elif direction == 'DOWN':
        if y + 1 < height:
            return x, y + 1
    else:
        raise ValueError('Dir must be LEFT, RIGHT, UP OR DOWN. Not a {}'.format(dir))
    return None


if __name__ == '__main__':
    main()
