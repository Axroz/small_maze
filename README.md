# MAZE

## Description

![Example maze image](maps/maze-task-first.svg)

This small script / software is to read, solve and output visual map of the route required to go 
through a maze. Result is printed out as a SVG map with route marked as red dots. Blue dot marks the start.
Green dot marks the finish.

All alternative exits are marked with black.

Start by inputing your mazes into maps folder. After you can execute the software from main.py

Program utilizes webbrowser and tries to open the created file. You can also find the result in the maps folder.

It is also possible to utilize your own location to read the maps from.



## How to run

### Pre-requisites and system info

This program has been created with Python 3.8.8

Environment is done with Anaconda and can be found from environment.yml
(This file might have some excess libraries, since I did not create it from clean install).

If you want to create an environment yourself here is the full list of required dependencies:
```python
import os
import typing
import webbrowser
from svgwrite import shapes, Drawing
from copy import deepcopy
```

### Starting software

Run main.py with your Python interpreter.
```commandline
python.exe main.py
```

There is a small text-based (input-prompt) UI where you can specify where to read the mazes.

You can also just input all the mazes into maps folder and run from there 
(it is presumed as a starting location).

## Modifications / Restrictions

Software cannot handle mazes that are not sized as NxM matrix. 
If such is tried the program will print out following error:
```
IndexError: Maze is probably not correctly formed!
```

Software cannot visualize mazes that are not solvable. (It would not be a big task to upgrade though)

Following mapping has been created in the program. This is used to read the map text files. 
Other input is not allowed and requires changes in the mapping.
```python
# Map the strings
BLOCK = '#'
EXIT = 'E'
START = '^'
SPACE = ' '
```

Test step counts are defined as a global variable. Changing this will define what steps are tested.
```python
TEST_STEPS = [20, 150, 200]
```

You can also alter the size of created SVG result by changing value for:
```python
MAZE_WALL_SIZE = 20
```

## TODO

* If we loop multiple files and solve puzzles in different max move variations,
 the program continues execution still though it is unnecessary
* Step count could be added to visualization