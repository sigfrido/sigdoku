
# TODO refactor as SudokuBoard class members???
class Dimensions(object):
    def __init__(self, root):
        try:
            introot = int(root)
            if not introot in Dimensions.valid_roots():
                raise ValueError('Bad root value')
            self._root = introot
            self._dimensions = self._root**2
        except:
            raise
            
    @classmethod
    def valid_roots(cls):
        return [2, 3, 4]
        

    @property
    def root(self):
        return self._root
        
    @property
    def dimensions(self):
        return self._dimensions
        
    @property
    def moves(self):
        return set(range(1, self._dimensions + 1))

dims = Dimensions(3)

ROOT = dims.root
DIMENSIONS = dims.dimensions
MOVES = dims.moves


class SudokuException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
        
class SudokuDeniedMove(SudokuException):
    pass

class Cell(object):
    
    def __init__(self):
        self._value = 0
        self._allowed_moves = MOVES.copy()
    
    def move(self, value):
        try:
            intvalue = self._check_move_value(value)
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
            
    def _check_move_value(self, value):
        try:
            intvalue = int(value)
            if intvalue < 0 or intvalue > DIMENSIONS:
                raise ValueError('Bad cell value : %d' % intvalue)
            return intvalue
        except:
            raise
    
    def clean(self):
        self.move(0)
        
    def value(self):
        return self._value
        
    def is_clean(self):
        return 0 == self._value
        
    def allowed_moves(self):
        return self._allowed_moves
        
    def is_allowed_move(self, value):
        return value in self.allowed_moves()
        
    def allow_move(self, value):
        # TODO check range
        self._allowed_moves.add(self._check_move_value(value))
        
    def deny_move(self, value):
        # TODO check range
        self._allowed_moves.remove(self._check_move_value(value))
        
        
        
class CellGroup(object):
    _cells = None
    
    def __init__(self):
        self._cells = []
        
    def add_cell(self, cell):
        if len(self._cells) == DIMENSIONS:
            raise IndexError('DIMENSIONS exceeded in group')
            
        if not isinstance(cell, Cell):
            raise Exception('This is not a Cell')
            
        self._cells.append(cell)
        
    def move(self, cell, value):
        self._cells[cell - 1].move(value)
        
    
    
class Board(object):
    
    def __init__(self):
        self._cells = []
        self._rows = self._makeCellGroups()
        self._cols = self._makeCellGroups()
        self._squares = self._makeCellGroups()
        
        # All zero-based
        for i in range(DIMENSIONS**2):
            cell = Cell()
            self._cells.append(cell)
            row = i / DIMENSIONS
            col = i % DIMENSIONS
            self._rows[row].add_cell(cell)
            self._cols[col].add_cell(cell)
            sqindex = i / ROOT
            
            
    def _makeCellGroups(self):
        cgs = []
        for i in range(DIMENSIONS):
            cgs.append(CellGroup())
        return cgs
        
    def cell(self, cellIndex):
        return self._cells[cellIndex]
        
    def row(self, rowIndex):
        return self._rows[rowIndex]
        
    def col(self, colIndex):
        return self._cols[colIndex]
        
    def square(self, squareIndex):
        return self._squares[squareIndex]
