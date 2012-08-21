
class Dimensions(object):
    """
    A Dimensions object defines the size of the sudoku board and the allowed moves
    """
    def __init__(self, root):
        try:
            introot = int(root)
            if not introot in Dimensions.valid_roots():
                raise ValueError('Bad root value')
            self._root = introot
            self._size = self._root**2
        except:
            raise
        
            
    @property
    def root(self):
        """
        For a typical sudoku board, root = 3
        """
        return self._root
        
        
    @classmethod
    def valid_roots(cls):
        return [2, 3, 4]
        
        
    @property
    def size(self):
        """
        The board size is the root value squared: 9 for a typical sudoku board
        """
        return self._size
        
        
    @property
    def moves(self):
        return set(range(1, self._size + 1))
        
        
    def check_move_value(self, value):
        try:
            intvalue = int(value)
            if intvalue < 0 or intvalue > self._size:
                raise ValueError('Bad move value : %d' % intvalue)
            return intvalue
        except:
            raise
    
        
class SudokuException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
        
class SudokuDeniedMove(SudokuException):
    pass

class Cell(object):
    
    def __init__(self, dimensions):
        self._value = 0
        self._dimensions = dimensions
        self._allowed_moves = self._dimensions.moves
    
    @property
    def dimensions(self):
        return self._dimensions
        
    @property
    def value(self):
        return self._value
                
    def move(self, value):
        try:
            intvalue = self.dimensions.check_move_value(value)
            if self._value == intvalue:
                return
            if intvalue:
                if not intvalue in self.allowed_moves():
                    raise SudokuDeniedMove('This value is denied for the cell')
            if self._value:
                #self.groups.allow(self._value)
                self._value = 0
            self._value = intvalue
            if self._value:
                #self.groups.deny(self._value)
                pass
        except:
            raise
            
    def clean(self):
        self.move(0)
        
    def is_clean(self):
        return 0 == self._value
        
    def allowed_moves(self):
        return self._allowed_moves
        
    def is_allowed_move(self, value):
        return value in self.allowed_moves()
        
    def allow_move(self, value):
        # TODO check range
        self._allowed_moves.add(self.dimensions.check_move_value(value))
        
    def deny_move(self, value):
        # TODO check range
        self._allowed_moves.remove(self.dimensions.check_move_value(value))
        
        
        
class CellGroup(object):
    
    def __init__(self, dimensions):
        self._cells = []
        self._dimensions = dimensions
        
    def add_cell(self, cell):
        if len(self._cells) == self._dimensions.size:
            raise IndexError('Dimensions exceeded in group')
            
        if not isinstance(cell, Cell):
            raise Exception('This is not a Cell')
            
        self._cells.append(cell)
        
    def move(self, index, value):
        self.cell(index).move(value)
        
    def cell(self, index):
        return self._cells[index - 1]
        
    
    
class Board(object):
    
    def __init__(self, root):

        self._dimensions = Dimensions(root)
        
        self._cells = []
        self._rows = self._makeCellGroups()
        self._cols = self._makeCellGroups()
        self._squares = self._makeCellGroups()
        
        # All zero-based
        for i in range(self.size**2):
            cell = Cell(self._dimensions)
            self._cells.append(cell)
            row = i / self.size
            col = i % self.size
            self._rows[row].add_cell(cell)
            self._cols[col].add_cell(cell)
            
            sqindex = i / self.root
            sqrow = sqindex / self.root / self.root
            sqcol = sqindex % self.root
            
            self._squares[sqrow*self.root + sqcol].add_cell(cell)
            
    @property
    def dimensions(self):
        return self._dimensions
        
    @property
    def size(self):
        return self._dimensions.size
                    
    @property
    def root(self):
        return self._dimensions.root
                    
    def _makeCellGroups(self):
        cgs = []
        for i in range(self.size):
            cgs.append(CellGroup(self.dimensions))
        return cgs
        
    def cell(self, cellIndex):
        return self._cells[cellIndex]
        
    def row(self, rowIndex):
        return self._rows[rowIndex]
        
    def col(self, colIndex):
        return self._cols[colIndex]
        
    def square(self, squareIndex):
        return self._squares[squareIndex]
