
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
            if self.board.finished():
                print "Game ended. Type n for a new game"
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
    
    def new_board(self, root):
        self.board = sudoku.Board(root)
        self.vertical_separator_every = self.board.root
        self.horizontal_separator_every = self.board.root
    
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
        for r in self.board._rows:
            row += 1
            result += self._render_cell_row(r, row)
            result += self._render_separator_row(row)
        return result
        
                
    def _render_cell_row(self, row, row_num):
        buf = (str(row_num) + self.vertical_separator).rjust(self.cell_width)
        col = 0
        for c in row._cells:
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
                (cell, value) = self.board.find_forced_move()
                if cell is None:
                    self._error_message = "No forced move cells"
                else:
                    cell.move(value)
            else:
                self._error_message = "Bad command: " + ' '.join(command_list)
                
        
    def move(self, row, col, value):
        self.board.row(row).cell(col).move(value)
        
        
        

if __name__ == '__main__':
    console = Console(2)
    console.play()
