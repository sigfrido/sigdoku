import sudoku
import unittest


class TestDimensions(unittest.TestCase):
    
    def test_check_dimensions_range(self):
        self.assertRaises(sudoku.SudokuRangeError, sudoku.Dimensions, 1)
        self.assertRaises(sudoku.SudokuRangeError, sudoku.Dimensions, 5)
        for root in sudoku.Dimensions.valid_roots():
            dim = sudoku.Dimensions(root)
            self.assertEqual(root, dim.root)
            self.assertEqual(root**2, dim.size)

    def test_check_move_value(self):
        dim = sudoku.Dimensions(3)
        
        self.assertRaises(sudoku.SudokuRangeError, dim.check_move_value, 11)
        self.assertRaises(sudoku.SudokuRangeError, dim.check_move_value, -1)
        self.assertRaises(ValueError, dim.check_move_value, 'Not an integer')
        for i in dim.moves:
            dim.check_move_value(i)
        
        
class TestCell(unittest.TestCase):

    def setUp(self):
        self.dims = sudoku.Dimensions(3)
        self.cell = sudoku.Cell(self.dims)
        
        
    def test_move(self):
        self.cell.move(5)
        self.assertEqual(self.cell.value, 5)

        # should raise an exception for illegal or out of range values
        self.assertRaises(ValueError, self.cell.move, 'Invalid move')
        self.assertRaises(sudoku.SudokuRangeError, self.cell.move, -1)
        self.assertRaises(sudoku.SudokuRangeError, self.cell.move, self.cell.dimensions.size + 1)
        
        
    def test_clean(self):
        self.cell.move(5)
        self.assertFalse(self.cell.is_clean())
        
        self.cell.clean()
        self.assertTrue(self.cell.is_clean())
        self.assertEqual(self.cell.value, 0)
        
        
    def test_allowed_moves(self):
        self.cell.clean()
        am = self.cell.allowed_moves()
        self.assertEqual(am, set([1,2,3,4,5,6,7,8,9]))
        
    def test_allow_move(self):
        self.cell.deny_move(5)
        self.assertFalse(self.cell.is_allowed_move(5), 'Move should be denied')

        self.cell.allow_move(5)
        self.assertTrue(self.cell.is_allowed_move(5), 'Move should be allowed')




class testCellGroup(unittest.TestCase):

    def setUp(self):
        self.dims = sudoku.Dimensions(3)
    
    def buildEmptyGroup(self):
        return sudoku.CellGroup(self.dims)
        
        
    def buildGroup(self):
        group = self.buildEmptyGroup()
        for i in self.dims.moves:
            group.add_cell(sudoku.Cell(self.dims))
        return group
        
            
    def test_empty_group(self):
        group = self.buildEmptyGroup()
        self.assertEqual(len(group._cells), 0)
        
        
    def test_group_dimensions(self):
        group = self.buildGroup()
        self.assertEqual(len(group._cells), self.dims.size)
        self.assertRaises(IndexError, group.add_cell, sudoku.Cell(self.dims))
        
        
    def test_bad_cell(self):
        group = self.buildEmptyGroup()
        group.add_cell(sudoku.Cell(self.dims))
        self.assertRaises(Exception, group.add_cell, 'This is not a cell')

        
    def test_two_groups(self):
        g1 = self.buildGroup()
        g2 = self.buildGroup()
        
        g1.move(1, 5)
        self.assertEqual(g1._cells[0].value, 5)
        
        g2.move(9, 5)
        self.assertEqual(g2._cells[8].value, 5)
        
        g1.move(1, 5)
        g2.move(1, 3)
        self.assertNotEqual(g1._cells[0].value, g2._cells[0].value)
        

class testBoard(unittest.TestCase):

    
    def setUp(self):
        self.board = sudoku.Board(3)

        
    def check_row_col_square(self, cell_global_index, row, col, square, cell_square_index):
        self.board._cells[cell_global_index - 1].move(5)
        self.assertEqual(5, self.board._rows[row - 1].cell(col).value)
        self.assertEqual(5, self.board._cols[col - 1].cell(row).value)
        self.assertEqual(5, self.board._squares[square - 1].cell(cell_square_index).value)
        
        
    def test_board_init(self):
        self.assertEqual(len(self.board._cells), 81)
        self.assertEqual(len(self.board._rows), 9)
        self.assertEqual(len(self.board._cols), 9)
        self.assertEqual(len(self.board._squares), 9)
        
        for cell in self.board._cells:
            self.assertEqual(0, cell.value)

        self.check_row_col_square(2, 1, 2, 1, 2)
        self.check_row_col_square(12, 2, 3, 1, 6)
        self.check_row_col_square(41, 5, 5, 5, 5)
        self.check_row_col_square(80, 9, 8, 9, 8)
        

if __name__ == '__main__':
    unittest.main()


