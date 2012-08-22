import sudoku
import unittest


class TestDimensions(unittest.TestCase):
    
    def test_check_dimensions_range(self):
        self.assertRaises(sudoku.OutOfRangeException, sudoku.Dimensions, 1)
        self.assertRaises(sudoku.OutOfRangeException, sudoku.Dimensions, 5)
        for root in sudoku.Dimensions.valid_roots():
            dim = sudoku.Dimensions(root)
            self.assertEqual(root, dim.root)
            self.assertEqual(root**2, dim.size)

    def test_check_move_value(self):
        dim = sudoku.Dimensions(3)
        
        self.assertRaises(sudoku.OutOfRangeException, dim.check_move_value, 11)
        self.assertRaises(sudoku.OutOfRangeException, dim.check_move_value, -1)
        self.assertRaises(ValueError, dim.check_move_value, 'Not an integer')
        for i in dim.moves:
            dim.check_move_value(i)
        
        
class TestCell(unittest.TestCase):

    def setUp(self):
        self.dims = sudoku.Dimensions(3)
        self.cell = sudoku.Cell(self.dims)
        
        
    def test_move_empty(self):
        self.cell.move(5)
        self.assertEqual(self.cell.value, 5)
        self.assertFalse(self.cell.is_empty())
        
        self.cell.empty()
        self.assertTrue(self.cell.is_empty())
        self.assertEqual(self.cell.value, 0)



    def test_move_bad_values(self):
        # Raise an exception for illegal or out of range values
        self.assertRaises(ValueError, self.cell.move, 'Invalid move - nonnumber')
        self.assertRaises(sudoku.OutOfRangeException, self.cell.move, -1)
        self.assertRaises(sudoku.OutOfRangeException, self.cell.move, self.cell.dimensions.size + 1)
        
        
    def test_move_allowed_on_empty_only(self):
        self.cell.move(5)
        self.assertRaises(sudoku.DeniedMoveException, self.cell.move, 4)
        self.assertRaises(sudoku.DeniedMoveException, self.cell.move, 5)
        
        self.cell.empty()
        self.cell.move(4)
        
        
        
    def test_allowed_moves(self):
        self.cell.empty()
        self.assertEqual(self.cell.allowed_moves(), set([1,2,3,4,5,6,7,8,9]))
        
        self.cell.deny_move(5)
        self.assertEqual(self.cell.allowed_moves(), set([1,2,3,4,6,7,8,9]))
        
        self.cell.deny_move(9)
        self.assertEqual(self.cell.allowed_moves(), set([1,2,3,4,6,7,8]))
        
        self.cell.deny_move(7)
        self.assertEqual(self.cell.allowed_moves(), set([1,2,3,4,6,8]))
        
        
    def test_allowed_moves_complete(self):
        am = range(1, 10)
        while True:
            self.assertEqual(self.cell.allowed_moves(), set(am))
            if not len(am):
                break
            self.cell.deny_move(am[0])
            am = am[1:]
        
        
    def test_allow_move(self):
        self.cell.deny_move(5)
        self.assertFalse(self.cell.is_allowed_move(5), msg = 'Move should be denied')

        self.cell.allow_move(5)
        self.assertTrue(self.cell.is_allowed_move(5), msg = 'Move should be allowed')



    def test_cell_listener(self):
        listener = TestCell.MockListener()
        self.cell.add_listener(listener)
        
        self.cell.move(5)
        self.assertEqual(5, listener.new_val)
        self.assertEqual(0, listener.old_val)
        
        self.cell.empty()
        self.assertEqual(0, listener.new_val)
        self.assertEqual(5, listener.old_val)
        
        
    class MockListener:
        old_val = -1
        new_val = -1
        
        def cell_changed(self, cell, old_value):
            self.old_val = old_value
            self.new_val = cell.value
                
        

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

        
    def test_cell_moves(self):
        group = self.buildGroup()
        
        group.move(1, 5)
        self.assertEqual(group._cells[0].value, 5)
        
        group.move(9, 6)
        self.assertEqual(group._cells[8].value, 6)
        
        self.assertRaises(sudoku.DeniedMoveException, group.move, 4, 6)

        
    def test_find_only_available_move(self):
        group = self.buildGroup()
        
        for i in range(1, 9):
            group.move(i, i)
            
        (cell, value) = group.find_only_available_move()
        
        self.assertEqual(9, value)
        self.assertEqual(cell, group.cell(9))
        
        
    def find_forced_move(self):
        group = self.buildGroup()

        # cell 1..6 => value 1..6
        for i in range(1, 7):
            group.move(i, i)
            
        group.cell(7).deny_move(8)
        group.cell(9).deny_move(8)
        
        (cell, value) = group.find_forced_move()
        
        self.assertEqual(8, value)
        self.assertEqual(cell, group.cell(8))
        
        

class testBoard(unittest.TestCase):

    
    def setUp(self):
        self.board = sudoku.Board(3)

        
    def check_row_col_square(self, cell_global_index, row, col, square, cell_square_index, value):
        self.board._cells[cell_global_index - 1].move(value)
        self.assertEqual(value, self.board._rows[row - 1].cell(col).value)
        self.assertEqual(value, self.board._cols[col - 1].cell(row).value)
        self.assertEqual(value, self.board._squares[square - 1].cell(cell_square_index).value)
        
        
    def test_init(self):
        self.assertEqual(len(self.board._cells), 81)
        self.assertEqual(len(self.board._rows), 9)
        self.assertEqual(len(self.board._cols), 9)
        self.assertEqual(len(self.board._squares), 9)
        
        for cell in self.board._cells:
            self.assertEqual(0, cell.value)

        self.check_row_col_square(2, 1, 2, 1, 2, 1)
        self.check_row_col_square(12, 2, 3, 1, 6, 2)
        self.check_row_col_square(41, 5, 5, 5, 5, 3)
        self.check_row_col_square(80, 9, 8, 9, 8, 4)
        
        
    def test_allow_move(self):
        
        self.board.row(1).cell(3).move(4)
        for i in range(1, 10):
            self.assertFalse(self.board.row(1).cell(i).is_allowed_move(4))
            self.assertFalse(self.board.col(3).cell(i).is_allowed_move(4))
            self.assertFalse(self.board.square(1).cell(i).is_allowed_move(4))
        

    def test_find_only_available_move(self):
        
        for i in range(1, 9):
            self.board.row(1).move(i, i)
            
        (cell, value) = self.board.find_only_available_move()
        
        self.assertEqual(9, value)
        self.assertEqual(cell, self.board.cell(9))
        
        
    def test_find_forced_move(self):

        # cell 1..6 => value 1..6
        for i in range(1, 7):
            self.board.row(1).move(i, i)
            
        self.board.row(4).cell(7).move(8)
        self.board.row(8).cell(9).move(8)
        
        (cell, value) = self.board.find_forced_move()
        
        self.assertEqual(8, value)
        self.assertEqual(cell, self.board.row(1).cell(8))
        
        # Test undo
        cell.move(8)
        cell.empty()
        
        (cell, value) = self.board.find_forced_move()
        
        self.assertEqual(8, value)
        self.assertEqual(cell, self.board.row(1).cell(8))
        
        


if __name__ == '__main__':
    unittest.main()


