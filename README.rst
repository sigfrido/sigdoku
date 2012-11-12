SIGDOKU
=======

OVERVIEW
--------

Self-teaching python and sudoku. Work in progress.

TODO
----

* switch from Class.method_name() to Class.methodName() convention
* think about allowed/denied moves: stick with Cell.deny_move(), or move responsibility out of
  Cell (possibly into CellGroup)?
* the "solver" can solve only basic sudoku games; need to implement more advanced techniques.
* use a Solver class (strategy pattern) instead of several CellGroup.find_*_move().


