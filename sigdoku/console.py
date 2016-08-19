# -*- coding: utf-8 -*-

import sudoku
import json
        
class Console(object):
    
    CELL_CHARS = '0123456789ABCDEFG'
    
    def __init__(self, root):
        self.solvers = sudoku.ALL_SOLVERS # config
        self.new_board(root)
        self.do_play = True
        self._error_message = ''
        self.render_separators = True
        self.cell_width = 3
        self.vertical_separator = '|'
        

    def play(self):
        while self.do_play:
            self.draw()
            self.check_finished()
            self.report_and_clear_error()
            self.get_command_and_execute()
            

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
        
            
    def get_command_and_execute(self):
        command_line = raw_input('Your move (row col value; h for help; q to quit): ').strip()
        self.execute_command_line(command_line)


    def new_board(self, root):
        self.board = sudoku.Board(root, self.solvers)
        self.vertical_separator_every = self.board.dimensions.root
        self.horizontal_separator_every = self.board.dimensions.root
    
    
    @property
    def error_message(self):
        return self._error_message

        
    def clear_error(self):
        self._error_message = ''
        
        
    def find_next_move(self):
        (cell, value) = self.board.find_move()
        if cell is None:
            self._error_message = "No move found"
            return False
        else:
            cell.move(value)
            return True
            
        
    def render(self):
        return  self._render_header_row() + \
                self._separator_row() + \
                self._render_cell_rows()

        
    def _render_header_row(self):
        result = self.vertical_separator.rjust(self.cell_width)
        for i in range(1, self.board.size + 1):
            result += self.CELL_CHARS[i].center(self.cell_width)
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
        buf = (self.CELL_CHARS[row_num] + self.vertical_separator).rjust(self.cell_width)
        col = 0
        for c in row.cells:
            col += 1
            buf += self._render_cell(c).center(self.cell_width)
            buf += self._render_vertical_separator(col)
        buf += "\n"
        return buf
        
        
    def _render_cell(self, cell):
        if cell.value:
            return self.CELL_CHARS[cell.value]
        else:
            return '.'
        
                    
    def execute_command_line(self, command_line):
        command_list = [tok for tok in command_line.split(' ') if tok != '']
        if not len(command_list):
            return
        try:
            [row, col, value] = [self.CELL_CHARS.find(tok.upper()) for tok in command_list]
            if row < 1 or col < 1:
                raise Exception
            self.board.move([(row, col, value)])
        except sudoku.SudokuException, descr:
            self._error_message = str(descr)
        except Exception, descr:
            self.execute_command(command_list)
            

    def execute_command(self, command_list):
        cmd = command_list[0][0].lower()
        method_name = "cmd_%s" % cmd
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            if callable(method):
                return method(command_list[1:])
        self._error_message = "Bad command: " + ' '.join(command_list)


    def cmd_h(self, params):        
        print """
<row> <col> <value> - place a value in a cell
q - Quit game
n [root] - new game with root dimension (root = 2|3|4)
f - Find next move
v - Solve game
i [row col] - interrogate cell
l [file] - Load a previously saved game (.json)
s [file] - Save game (.json)
h - print help
"""


    def cmd_q(self, params):
        self.do_play = False
        
        
    def cmd_n(self, params):
        try:
            root = int(params[0])
        except:
            root = 3
        self.new_board(root)
        
        
    def cmd_i(self, params):
        try:
            [row, col] = [self.CELL_CHARS.find(tok.upper()) for tok in params]
            print "Cell(%d, %d): %s" % (row, col, self.board.row(row).cell(col).allowed_moves())
        except:
            self._error_message = "Cannot find cell %s" %params

        
    # find move
    def cmd_f(self, params):
        self.find_next_move()


    # Solve game        
    def cmd_v(self, params):
        return self.board.solve()
        
        
    def cmd_l(self, params):
        try:
            with open(params[0], 'r') as f:
                data = json.load(f)
                self.new_board(data['dim'])
                self.board.move(data['moves'])
        except Exception, e:
            self._error_message = 'Impossibile aprire il file: %s' % e
            

    def cmd_s(self, params):
        try:
            data = {}
            data['dim'] = self.board.dimensions.root
            data['moves'] = self.board.moves[:]
            with open(params[0], 'w') as f:
                json.dump(data, f)
        except Exception, e:
            self._error_message = 'Impossibile salvare il file: %s' % e
                    
        

if __name__ == '__main__':
    console = Console(3)
    console.play()
