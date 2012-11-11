
import sudoku
        
class Console(object):
    
    def __init__(self, root):
        self.new_board(root)
        self.do_play = True
        self._error_message = ''
        self.render_separators = True
        self.cell_width = 4
        self.vertical_separator = '|'
        

    # Interactive (non-testable) commands
        
    def play(self):
        while self.do_play:
            self.draw()
            self.check_finished()
            self.report_and_clear_error()
            self.get_command_line()
            

    def draw(self):
        print self.render()
        

    def check_finished(self):
        if self.board.finished():
            print "Game ended. Type n for a new game"
            return True
        return False

    def report_and_clear_error(self):
        if self.error_message:
            print self.error_message
            self.clear_error()
        
            
    def get_command_line(self):
        command_line = raw_input('Your move (row col value; h for help; q to quit): ').strip()
        self.parse_command_line(command_line)


    # End of interactive commands
    
    def new_board(self, root):
        self.board = sudoku.Board(root)
        self.vertical_separator_every = self.board.dimensions.root
        self.horizontal_separator_every = self.board.dimensions.root
    
    @property
    def error_message(self):
        return self._error_message
        
    def clear_error(self):
        self._error_message = ''
        
        
    def render(self):
        return  self._render_header_row() + \
                self._separator_row() + \
                self._render_cell_rows()
        
    def _render_header_row(self):
        result = self.vertical_separator.rjust(self.cell_width)
        for i in range(1, self.board.size + 1):
            result += str(i).center(self.cell_width)
            result += self._render_vertical_separator(i)
        result += "\n"
        return result
        

    def _render_vertical_separator(self, index):
        if self.render_separators and index % self.vertical_separator_every == 0:
            return self.vertical_separator
        return ''
        
                
    def _render_separator_row(self, row):
        if self.render_separators and row % self.horizontal_separator_every == 0:
            return self._separator_row()
        return ''

        
    def _separator_row(self):
        return ''.ljust(self.cell_width * (self.board.size + 1) + \
            int(self.render_separators) * self.vertical_separator_every, '-') + "\n"


    def _render_cell_rows(self):
        row = 0
        result = ''
        for r in self.board.rows:
            row += 1
            result += self._render_cell_row(r, row)
            result += self._render_separator_row(row)
        return result
        
                
    def _render_cell_row(self, row, row_num):
        buf = (str(row_num) + self.vertical_separator).rjust(self.cell_width)
        col = 0
        for c in row.cells:
            col += 1
            buf += self._render_cell(c).center(self.cell_width)
            buf += self._render_vertical_separator(col)
        buf += "\n"
        
        return buf
        
        
    def _render_cell(self, cell):
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
            
        except sudoku.SudokuException, descr:
            self._error_message = str(descr)
            
        except Exception, descr:
            self.execute_command(command_list)
            

    def execute_command(self, command_list):
            cmd = command_list[0]
            
            if cmd == 'q':
                self.do_play = False
            elif cmd == 'n':
                try:
                    root = int(command_list[1])
                except:
                    root = 3
                self.new_board(root)
            elif cmd == 'f':
                self.find_next_move()
            elif cmd == 's':
                self.solve()
            elif cmd == 'h':
                print """
<row> <col> <value> - place a value in a cell
q - Quit game
n [root] - new game with root dimension (root = 2|3|4)
f - Find next forced move
h - print help
"""
                
            else:
                self._error_message = "Bad command: " + ' '.join(command_list)
                
    
    def move(self, row, col, value):
        self.board.row(row).cell(col).move(value)
        
        
    def solve(self):
        while(self.find_next_move()):
            if self.check_finished():
                return True
        return False
    
    
    def find_next_move(self):
        (cell, value) = self.board.find_move()
        if cell is None:
            self._error_message = "No forced move found"
            return False
        else:
            cell.move(value)
            return True
            
        

if __name__ == '__main__':
    console = Console(3)
    console.play()