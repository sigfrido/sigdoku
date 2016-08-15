# -*- coding: utf-8 -*-

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
        
        
    @property
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
        self.allow_all_moves()
        self.__listeners = []
    
    
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
        
        
    def empty(self):
        self.move(0)
    
        
    def is_empty(self):
        return 0 == self.__value
    
        
    def allowed_moves(self):
        return self._allowed_moves
    
        
    def is_allowed_move(self, value):
        return value in self.allowed_moves()
        
        
    def allow_all_moves(self):
        self._allowed_moves = self.dimensions.all_moves


    def deny_move(self, value):
        value = self.dimensions.get_int_in_range(value)
        if value in self._allowed_moves:
            self._allowed_moves.remove(value)

        
        
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
        return self.__cells[index - 1]
        
        
    @property
    def cells(self):
        return self.__cells
        
        
    @property
    def dimensions(self):
        return self.__dimensions
        
        
    # TODO create Move class
    
class CellGroup(BaseCellGroup):
    
    def __init__(self, dimensions):
        super(CellGroup, self).__init__(dimensions)
        self.allow_all_moves()

        
    def deny_move(self, value, source_cell):
        for c in self.cells:
            c.deny_move(value)
        self._allowed_moves.remove(value)
        

    def allow_all_moves(self):
        self._allowed_moves = self.dimensions.all_moves


    def allowed_moves(self):
        return self._allowed_moves
        
        
    def cell_changed(self, cell, old_value):
        if cell.value:
            self.deny_move(cell.value, cell)
        
    
    
class Board(BaseCellGroup):
    
    def __init__(self, root, solvers=[]):
        super(Board, self).__init__(Dimensions(root))

        self.__rows = self.__makeCellGroups()
        self.__cols = self.__makeCellGroups()
        self.__squares = self.__makeCellGroups()
        self.__solvers = list(solvers)[:]

        cells_per_facet = self.dimensions.size
        cells_per_board = cells_per_facet**2        
        cells_per_square_facet = root
        
        # All zero-based
        for cell_index in range(cells_per_board):
            cell = Cell(self.dimensions)
            self.add_cell(cell)
            
            board_row = cell_index / cells_per_facet
            board_col = cell_index % cells_per_facet
            self.__rows[board_row].add_cell(cell)
            self.__cols[board_col].add_cell(cell)
            
            cell_square_index = cell_index / cells_per_square_facet
            square_row = cell_square_index / cells_per_square_facet / cells_per_square_facet
            square_col = cell_square_index % cells_per_square_facet
            
            square_index = square_row*cells_per_square_facet + square_col
            self.__squares[square_index].add_cell(cell)
            
        self.__empty_cells = cells_per_board
           
            
    @property
    def size(self):
        return self.dimensions.size


    @property
    def num_cells(self):
        return self.dimensions.size**2

           
    def __makeCellGroups(self):
        cgs = []
        for i in range(self.dimensions.size):
            cgs.append(CellGroup(self.dimensions))
        return cgs
        
        
    def row(self, rowIndex):
        return self.__rows[rowIndex - 1]
        
        
    def col(self, colIndex):
        return self.__cols[colIndex - 1]
        
        
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


    def cell_changed(self, cell, old_value):
        if cell.value:
            self.__empty_cells -= 1
        else:
            self.__empty_cells += 1
            self.recalc_allowed_moves()


    def finished(self):
        return 0 == self.__empty_cells


    def recalc_allowed_moves(self):
        self.__empty_cells = self.num_cells
        
        for cell in self.cells:
            cell.allow_all_moves()
        for group in self.all_groups:
                group.allow_all_moves()
        for cell in self.cells:
            if cell.value:
                cell.changed(0)
        
        
    @property
    def all_groups(self):
        return self.__rows + self.__cols + self.__squares


    def find_move(self):
        for solver in self.__solvers:
            (c, v) = solver.find_move(self)
            if c is not None:
                return (c, v)
        return (None, None)
        
        
        
class BaseSolver(object):
    """
    Returns compulsory moves
    """
    def find_move(self, board_or_group):
        if isinstance(board_or_group, Board):
            groups = board_or_group.all_groups
        else:
            groups = [board_or_group]
        for group in groups:
            for c in group.cells:
                if not c.value:
                    if len(c.allowed_moves()) == 1:
                        return (c, list(c.allowed_moves())[0])
            for value in group.allowed_moves():
                cell = None
                for c in group.cells:
                    if not c.value and c.is_allowed_move(value):
                        if cell is None:
                            cell = c
                        else:
                            cell = None
                            break
                if not cell is None:
                    return (cell, value)
            return (None, None)
            

        
        
