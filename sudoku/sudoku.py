
class SudokuException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
        
class SudokuDeniedMove(SudokuException):
    pass

class SudokuBlockedMove(SudokuException):
    pass

class SudokuRangeError(SudokuException):
    pass


class Dimensions(object):
    """
    A Dimensions object defines the size of the sudoku board and the allowed moves
    """
    def __init__(self, root):
        try:
            introot = int(root)
            if not introot in Dimensions.valid_roots():
                raise SudokuRangeError('Bad root value: {root}'.format(root=root))
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
                raise SudokuRangeError('Bad move value: %d' % intvalue)
            return intvalue
        except:
            raise
    
        
class Cell(object):
    """
    A board cell
    """
    
    def __init__(self, dimensions):
        self._value = 0
        self._dimensions = dimensions
        self._allowed_moves = self.dimensions.moves
        self._listeners = []
    
    
    @property
    def dimensions(self):
        return self._dimensions
    
        
    @property
    def value(self):
        return self._value
    
                
    def move(self, value):
        try:
            intvalue = self.dimensions.check_move_value(value)
            if self._value and intvalue:
                raise SudokuBlockedMove('The cell has already a value')
                
            if self._value == intvalue:
                return
                
            if intvalue:
                if not intvalue in self.allowed_moves():
                    raise SudokuDeniedMove('This value is denied for the cell')
                    
            if self._value:
                old_value = self._value
                self._value = 0
                self.changed(old_value)
                if not intvalue:
                    return
                
            self._value = intvalue
            self.changed(0)
        except:
            raise
    
    
    def changed(self, old_value):
        for g in self._listeners:
            g.cell_changed(self, old_value)
            
    
    def add_listener(self, group):
        self._listeners.append(group)
        
        
    def empty(self):
        self.move(0)
    
        
    def is_empty(self):
        return 0 == self._value
    
        
    def allowed_moves(self):
        return self._allowed_moves
    
        
    def is_allowed_move(self, value):
        return value in self.allowed_moves()
        
        
    def allow_move(self, value):
        self._allowed_moves.add(self.dimensions.check_move_value(value))
        
        
    def deny_move(self, value):
        value = self.dimensions.check_move_value(value)
        if value in self._allowed_moves:
            self._allowed_moves.remove(value)
        
        
        
class CellGroup(object):
    
    def __init__(self, dimensions):
        self._cells = []
        self._dimensions = dimensions
        self._allowed_moves = self._dimensions.moves

        
    def add_cell(self, cell):
        if len(self._cells) == self._dimensions.size:
            raise IndexError('Dimensions exceeded in group')
            
        if not isinstance(cell, Cell):
            raise Exception('This is not a Cell')
            
        self._cells.append(cell)
        cell.add_listener(self)

        
    def move(self, index, value):
        self.cell(index).move(value)

        
    def cell(self, index):
        index = self._dimensions.check_move_value(index)
        return self._cells[index - 1]
        
        
    def deny_move(self, value, source_cell):
        for c in self._cells:
            c.deny_move(value)
        self._allowed_moves.remove(value)
        

    def allow_move(self, value, source_cell):
        for c in self._cells:
            c.allow_move(value)
        self._allowed_moves.add(value)
        
    def allowed_moves(self):
        return self._allowed_moves
        

    # TODO refactor to a template method in a base class
    def cell_changed(self, cell, old_value):
        if (not old_value) and cell.value:
            self.deny_move(cell.value, cell)
        elif old_value and (not cell.value):
            self.allow_move(old_value, cell)
        else:
            raise Exception('cell_changed with same values')
            
    # TODO create Move class
    def find_only_available_move(self):
        # Same bas impl - TODO factor out
        for c in self._cells:
            if not c.value:
                if len(c.allowed_moves()) == 1:
                    return (c, list(c.allowed_moves())[0])
                    
        return (None, None)
        
        
            
    def find_forced_move(self):

        for value in self.allowed_moves():
            cell = None
            for c in self._cells:
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

        self._dimensions = Dimensions(root)
        
        self._cells = []
        self._rows = self._makeCellGroups()
        self._cols = self._makeCellGroups()
        self._squares = self._makeCellGroups()
        
        # All zero-based
        for i in range(self.size**2):
            cell = Cell(self._dimensions)
            self._cells.append(cell)
            cell.add_listener(self)
            
            row = i / self.size
            col = i % self.size
            self._rows[row].add_cell(cell)
            self._cols[col].add_cell(cell)
            
            sqindex = i / self.root
            sqrow = sqindex / self.root / self.root
            sqcol = sqindex % self.root
            
            self._squares[sqrow*self.root + sqcol].add_cell(cell)
            
        self._empty_cells = self.size**2
           
            
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
        return self._cells[cellIndex - 1]
        
        
    def row(self, rowIndex):
        return self._rows[rowIndex - 1]
        
        
    def col(self, colIndex):
        return self._cols[colIndex - 1]
        
        
    def square(self, squareIndex):
        return self._squares[squareIndex - 1]


    def cell_changed(self, cell, old_value):
        if (not old_value) and cell.value:
            self._empty_cells -= 1
        elif old_value and (not cell.value):
            self._empty_cells += 1
        else:
            raise Exception('cell_changed with same values')


    def finished(self):
        return 0 == self._empty_cells


    # TODO create Move class
    def find_only_available_move(self):
        # Same bas impl - TODO factor out
        for c in self._cells:
            if not c.value:
                if len(c.allowed_moves()) == 1:
                    return (c, list(c.allowed_moves())[0])
                    
        return (None, None)


    def find_forced_move(self):
        (c, v) = self.find_only_available_move()
        if c is not None:
            return (c, v)
                    
        for grouparray in [self._rows, self._cols, self._squares]:
            for group in grouparray:
                (c, v) = group.find_forced_move()
                if not c is None:
                    return (c, v)
                    
        return (None, None)
