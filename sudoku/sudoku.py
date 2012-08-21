DIMENSIONS = 9
ROOT = 3


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
        self._allowed_moves = set(range(1, DIMENSIONS + 1))
    
    def move(self, value):
        try:
            intvalue = int(value)
            if intvalue < 0 or intvalue > DIMENSIONS:
                raise ValueError('Bad cell value : %d' % intvalue)
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
        self._allowed_moves.add(value)
        
    def deny_move(self, value):
        # TODO check range
        self._allowed_moves.remove(value)
        
        
        
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
