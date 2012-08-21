
class SudokuException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
        
class SudokuDeniedMove(SudokuException):
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
        return self._cells[cellIndex - 1]
        
    def row(self, rowIndex):
        return self._rows[rowIndex - 1]
        
    def col(self, colIndex):
        return self._cols[colIndex - 1]
        
    def square(self, squareIndex):
        return self._squares[squareIndex - 1]
        
        
        
class Console(object):
    
    def __init__(self, root):
        self.board = Board(root)
        self.do_play = True
        self._error_message = ''
        

    # Interactive (non-testable) commands
        
    def play(self):
        while self.do_play:
            self.draw()
            self.report_and_clear_error()
            self.get_command_line()
            

    def draw(self):
        print self.render()
        
        
    def report_and_clear_error(self):
        if self.error_message:
            print self.error_message
            self.clear_error()
            
    def get_command_line(self):
        command_line = raw_input('Your move (row col value; q to quit): ').strip()
        self.parse_command_line(command_line)


    # End of interactive commands
    
    
    @property
    def error_message(self):
        return self._error_message
        
    def clear_error(self):
        self._error_message = ''
        
        
    def render(self):
        width = 4
        
        result = ''.center(width)
        for i in range(1, self.board.size + 1):
            result += str(i).center(width)
        result += "\n"
        result += ''.ljust(width * (self.board.size + 1), '-') + "\n"
        row = 0
        for r in self.board._rows:
            row += 1
            buf = (str(row) + '|').rjust(width)
            for c in r._cells:
                buf += self._cellvalue(c).center(width)
            result += buf + "\n"
        return result
        
                
    def _cellvalue(self, cell):
        if cell.value:
            return str(cell.value)
        else:
            return '.'
        
                    
    def parse_command_line(self, command_line):
        command_list = [tok for tok in command_line.split(' ') if tok != '']
        self.parse_command_list(command_list)
        
        
    def parse_command_list(self, command_list):
        if not len(command_list):
            return
            
        try:
            [row, col, value] = [int(c) for c in command_list if c <> '']
            self.move(row, col, value)
            
        except SudokuException, descr:
            self._error_message = str(descr)
            
        except Exception, descr:
            self.execute_command(command_list)
            

    def execute_command(self, command_list):
            cmd = command_list[0]
            
            if cmd == 'q':
                self.do_play = False
            else:
                self._error_message = "Bad command: " + ' '.join(command_list)
                
        
    def move(self, row, col, value):
        self.board.row(row).cell(col).move(value)
        
        
        

if __name__ == '__main__':
    console = Console(3)
    console.play()
