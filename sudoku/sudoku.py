
class SudokuException(Exception):
    
    def __init__(self, value):
        self.value = value
        
        
    def __str__(self):
        return repr(self.value)
        
        
class DeniedMoveException(SudokuException):
    
    pass


class OutOfRangeException(SudokuException):
    
    def __init__(self, value):
        try:
            self.value = 'Value out of range: %d' % value
        except:
            # In case value is a string
            self.value = value



class Dimensions(object):
    """
    A Dimensions object defines the size of the sudoku board as well as the range of the allowed moves
    """

    VALID_ROOTS = [2, 3, 4]
    

    def __init__(self, root):
        try:
            introot = int(root)
            if not introot in Dimensions.VALID_ROOTS:
                raise OutOfRangeException(root)
            self.__root = introot
            self.__size = self.__root**2
        except:
            raise
        
            
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
            if intvalue < 0 or intvalue > self.__size:
                raise OutOfRangeException(intvalue)
            return intvalue
        except:
            # TODO: raise a SudokuException anyway?
            raise # ValueError
    
        
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
            
        if self.__value == intvalue:
            return
            
        if intvalue:
            if not intvalue in self.allowed_moves():
                raise DeniedMoveException('This value is denied for the cell')
            self.__value = intvalue
            self.changed(0)
        else:
            old_value = self.__value
            self.__value = 0
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
        
        
        
class CellGroup(object):
    
    def __init__(self, dimensions):
        self.__cells = []
        self.__dimensions = dimensions
        self.allow_all_moves()  

        
    def add_cell(self, cell):
        if len(self.__cells) == self.__dimensions.size:
            raise IndexError('Dimensions exceeded in group')
            
        if not isinstance(cell, Cell):
            raise Exception('This is not a Cell')
            
        self.__cells.append(cell)
        cell.add_listener(self)

        
    def cell(self, index):
        index = self.__dimensions.get_int_in_range(index)
        return self.__cells[index - 1]
        
        
    @property
    def cells(self):
        return self.__cells
        
        
    def deny_move(self, value, source_cell):
        for c in self.__cells:
            c.deny_move(value)
        self._allowed_moves.remove(value)
        

    def allowed_moves(self):
        return self._allowed_moves
        
        
    def allow_all_moves(self):
        self._allowed_moves = self.__dimensions.all_moves


    # TODO refactor to a template method in a base class
    def cell_changed(self, cell, old_value):
        if cell.value:
            self.deny_move(cell.value, cell)
            
            
    # TODO create Move class
    def find_only_available_move(self):
        # Same bas impl - TODO factor out
        for c in self.__cells:
            if not c.value:
                if len(c.allowed_moves()) == 1:
                    return (c, list(c.allowed_moves())[0])
                    
        return (None, None)
        
                    
    def find_forced_move(self):

        for value in self.allowed_moves():
            cell = None
            for c in self.__cells:
                if not c.value and c.is_allowed_move(value):
                    if cell is None:
                        cell = c
                    else:
                        cell = None
                        break
            if not cell is None:
                return (cell, value)
                
        return (None, None)
            
    
        
    
    
class Board(object):
    
    def __init__(self, root):

        self.__dimensions = Dimensions(root)
        self.__cells = []
        self._rows = self._makeCellGroups()
        self._cols = self._makeCellGroups()
        self._squares = self._makeCellGroups()

        cells_per_facet = self.__dimensions.size
        cells_per_board = cells_per_facet**2        
        cells_per_square_facet = root
        
        # All zero-based
        for cell_index in range(cells_per_board):
            cell = Cell(self.dimensions)
            self.__cells.append(cell)
            cell.add_listener(self)
            
            board_row = cell_index / cells_per_facet
            board_col = cell_index % cells_per_facet
            self._rows[board_row].add_cell(cell)
            self._cols[board_col].add_cell(cell)
            
            cell_square_index = cell_index / cells_per_square_facet
            square_row = cell_square_index / cells_per_square_facet / cells_per_square_facet
            square_col = cell_square_index % cells_per_square_facet
            
            square_index = square_row*cells_per_square_facet + square_col
            self._squares[square_index].add_cell(cell)
            
        self.__empty_cells = cells_per_board
           
            
    @property
    def dimensions(self):
        return self.__dimensions
        
        
    @property
    def size(self):
        return self.dimensions.size
           
                    
    def _makeCellGroups(self):
        cgs = []
        for i in range(self.size):
            cgs.append(CellGroup(self.dimensions))
        return cgs
        
        
    def cell(self, cellIndex):
        return self.__cells[cellIndex - 1]
        
        
    @property
    def cells(self):
        return self.__cells
        
        
    def row(self, rowIndex):
        return self._rows[rowIndex - 1]
        
        
    def col(self, colIndex):
        return self._cols[colIndex - 1]
        
        
    def square(self, squareIndex):
        return self._squares[squareIndex - 1]


    def cell_changed(self, cell, old_value):
        if cell.value:
            self.__empty_cells -= 1
        else:
            self.__empty_cells += 1
            self.recalc_allowed_moves()


    def finished(self):
        return 0 == self.__empty_cells


    def recalc_allowed_moves(self):
        for cell in self.__cells:
            cell.allow_all_moves()
        for group in self.all_groups:
                group.allow_all_moves()
        for cell in self.__cells:
            if cell.value:
                cell.changed(0)
        
        
    # TODO create Move class
    def find_only_available_move(self):
        # Same bas impl - TODO factor out
        for c in self.__cells:
            if not c.value:
                if len(c.allowed_moves()) == 1:
                    return (c, list(c.allowed_moves())[0])
                    
        return (None, None)
        

    @property
    def all_groups(self):
        return self._rows + self._cols + self._squares


    def find_forced_move(self):
        (c, v) = self.find_only_available_move()
        if c is not None:
            return (c, v)
                    
        for group in self.all_groups:
            (c, v) = group.find_forced_move()
            if not c is None:
                return (c, v)
                    
        return (None, None)
