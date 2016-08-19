# SIGDOKU

## OVERVIEW

Sigdoku is a Sudoku solver in python. It allows for 4x4, 9x9 or 16x16 boards.

It is a playfield for learning Sudoku and python programming techniques.

It has a basic text console which can be run with:

```
python console.py
```

Type h for help when in concole.

To use the sudoku.Board class:

```
import sudoku

board = sudoku.Board()
board.move([
    [1, 2, 6], [1, 5, 3], [1, 8, 9], [2, 1, 7], 
    [2, 3, 5], [2, 5, 6], [3, 6, 2], [4, 2, 4], 
    [4, 7, 6], [4, 9, 8], [5, 1, 8], [5, 4, 9], 
    [5, 5, 4], [5, 6, 3], [5, 7, 2], [6, 2, 7], 
    [6, 4, 6], [6, 9, 3], [7, 6, 7], [7, 8, 8], 
    [7, 9, 6], [8, 1, 2], [8, 3, 4], [8, 7, 7], 
    [9, 3, 7], [9, 4, 8], [9, 5, 5]
])
board.solve()
print board.dump()
168734592
725169834
493582167
349275618
816943275
572618943
951427386
284396751
637851429
```
 

## TODO

* Better console comand line
* Use plain text instead of json for loading / saving games
* Still needs a solver class for advanced games
