# -*- coding: utf-8 -*-
import solvers

class SudokuException(Exception):
    """
    Base class for all sudoku exceptions
    """
    pass


    
class DeniedMoveException(SudokuException):
    """
    User attempted a denied move
    """
    pass



class OutOfRangeException(SudokuException):
    """
    User specified an out of range value
    """
    pass



class Dimensions(object):
    """
    A Dimensions object defines the size of the sudoku board and the range 
    of the allowed moves
    """
    VALID_ROOTS = [2, 3, 4]

    def __init__(self, root):
        try:
            introot = int(root)
            if introot in Dimensions.VALID_ROOTS:
                self.__root = introot
                self.__size = self.__root**2
                self.ALL_MOVES = list(self.all_moves())
                return
        except:
            pass
        raise OutOfRangeException("Root dimension not in range 2..4: %s" % root)
        
            
    @property
    def root(self):
        """
        For a typical sudoku board, root = 3
        """
        return self.__root
        
        
    @property
    def size(self):
        """
        The board size is the root value squared: 9 for a typical sudoku board
        """
        return self.__size
        
        
    def all_moves(self):
        return set(range(1, self.__size + 1))
        
        
    def get_int_in_range(self, value):
        try:
            intvalue = int(value)
            if intvalue >= 0 and intvalue <= self.__size:
                return intvalue
        except:
            pass
        raise OutOfRangeException("Value not in range 0..%d: %s" % (self.__size, value))



class Cell(object):
    """
    A board cell
    """
    
    def __init__(self, dimensions):
        self.__value = 0
        self.__dimensions = dimensions
        self.__listeners = []
        self.__groups = []
        self.row = None
        self.col = None
        self.square = None


    @property
    def dimensions(self):
        return self.__dimensions
    
        
    @property
    def value(self):
        return self.__value
    
                
    def move(self, value):
        intvalue = self.dimensions.get_int_in_range(value)
        if self.__value and intvalue:
            raise DeniedMoveException('The cell has already a value')
        if intvalue:
            if not intvalue in self.allowed_moves():
                raise DeniedMoveException('This value is denied for the cell')
            self.__value = intvalue
            self.changed(0)
        else:
            old_value, self.__value = self.__value, 0
            self.changed(old_value)
    
    
    def changed(self, old_value):
        for g in self.__listeners:
            g.cell_changed(self, old_value)
            
    
    def add_listener(self, group):
        self.__listeners.append(group)
        

    def add_group(self, group):
        self.__groups.append(group)
        
        
    def empty(self):
        self.move(0)
    
        
    def is_empty(self):
        return 0 == self.__value
    
        
    def allowed_moves(self):
        return set.intersection(
            *[group.allowed_moves() for group in self.__groups]
        ) if not self.value else set()
        
        

class BaseCellGroup(object):

    def __init__(self, dimensions):
        self.__cells = []
        self.__dimensions = dimensions
        
        
    @property
    def num_cells(self):
        return self.__dimensions.size

    
    def cell_changed(self, cell, old_value):
        pass
        
        
    def add_cell(self, cell):
        if len(self.__cells) == self.num_cells:
            raise IndexError('Dimensions exceeded in group')
        if not isinstance(cell, Cell):
            raise Exception('This is not a Cell')
        self.__cells.append(cell)
        cell.add_listener(self)
        
        
    def cell(self, index):
        return self.__cells[self.dimensions.get_int_in_range(index) - 1]
        
        
    @property
    def cells(self):
        return self.__cells
        
        
    @property
    def dimensions(self):
        return self.__dimensions
        
        
    def allowed_moves_for_cells(self):
        return dict((cell, cell.allowed_moves()) for cell in self.cells) #  if not cell.value
        



class CellGroup(BaseCellGroup):
    
    def __init__(self, dimensions):
        super(CellGroup, self).__init__(dimensions)
        self.index = None


    def add_cell(self, cell):
        super(CellGroup, self).add_cell(cell)
        cell.add_group(self)

        
    def allowed_moves(self):
        return self.dimensions.all_moves().difference(
            set([cell.value for cell in self.cells])
        )

        
        
class Square(CellGroup):

    def __init__(self, dimensions):
        super(Square, self).__init__(dimensions)
        self.rows = []
        self.cols = []
    
        
    
# Convenience global with all the solvers in the right order
ALL_SOLVERS = [solvers.BaseSolver(), solvers.RowColInSquareSolver(), solvers.CoupleTripletInGroupSolver()]
    
class Board(BaseCellGroup):
    
    def __init__(self, root=3, solvers=ALL_SOLVERS):
        super(Board, self).__init__(Dimensions(root))

        self.__rows = self.__makeCellGroups()
        self.__cols = self.__makeCellGroups()
        self.__squares = self.__makeCellGroups(Square)
        self.__solvers = list(solvers)[:]
        self.__moves = []

        cells_per_facet = self.dimensions.size
        cells_per_board = cells_per_facet**2        
        cells_per_square_facet = root
        
        # All zero-based
        for cell_index in range(cells_per_board):
            cell = Cell(self.dimensions)

            board_row = cell_index / cells_per_facet
            board_col = cell_index % cells_per_facet
            self.__rows[board_row].add_cell(cell)
            self.__cols[board_col].add_cell(cell)
            cell.row = board_row + 1
            cell.col = board_col + 1
            
            cell_square_index = cell_index / cells_per_square_facet
            square_row = cell_square_index / cells_per_square_facet / cells_per_square_facet
            square_col = cell_square_index % cells_per_square_facet
            square_index = square_row*cells_per_square_facet + square_col
            square = self.__squares[square_index]
            square.add_cell(cell)
            if not cell.row in square.rows:
                square.rows.append(cell.row)
            if not cell.col in square.cols:
                square.cols.append(cell.col)
            cell.square = square_index + 1
            
            # We need board listener being called last
            self.add_cell(cell)

            
    @property
    def size(self):
        return self.dimensions.size


    @property
    def num_cells(self):
        return self.dimensions.size**2

          
    def move(self, moves):
        for (row, col, value) in moves:
            self.row(row).cell(col).move(value)


    def __makeCellGroups(self, clazz=CellGroup):
        cgs = []
        for i in range(self.dimensions.size):
            cgs.append(clazz(self.dimensions))
            cgs[i].index = i + 1
        return cgs
        
        
    def cell(self, index):
        return self.cells[index - 1]


    def row(self, rowIndex):
        return self.__rows[self.dimensions.get_int_in_range(rowIndex) - 1]
        
        
    def col(self, colIndex):
        return self.__cols[self.dimensions.get_int_in_range(colIndex) - 1]
        
        
    def square(self, squareIndex):
        return self.__squares[squareIndex - 1]
        
    
    @property    
    def rows(self):
        return self.__rows
        
        
    @property
    def cols(self):
        return self.__cols
        
    
    @property
    def squares(self):
        return self.__squares
        
        
    @property
    def moves(self):
        return self.__moves


    def cell_changed(self, cell, old_value):
        self.__moves.append((cell.row, cell.col, cell.value))


    @property
    def all_groups(self):
        return self.__rows + self.__cols + self.__squares


    def find_move(self):
        allowed_moves = self.allowed_moves_for_cells()
        for solver in self.__solvers:
            (c, v) = solver.find_move(self, allowed_moves)
            if c is not None:
                return (c, v)
        return (None, None)
        
        
    def finished(self):
        return all([cell.value for cell in self.cells])


    def solve(self):
        while not self.finished():
            (cell, value) = self.find_move()
            if cell is None:
                return False
            else:
                cell.move(value)
        return True
        
        
    def dump(self):
        return '\n'.join([''.join([str(cell.value) for cell in row.cells]) for row in self.rows])
            
            
