# -*- coding: utf-8 -*-

import sudoku
import unittest


class TestDimensions(unittest.TestCase):
    
    def test_check_dimensions_range(self):
        self.assertRaises(sudoku.OutOfRangeException, sudoku.Dimensions, 1)
        self.assertRaises(sudoku.OutOfRangeException, sudoku.Dimensions, 5)
        self.assertRaises(sudoku.OutOfRangeException, sudoku.Dimensions, 'Bad root value - nonnumber')
        
        for root in sudoku.Dimensions.VALID_ROOTS:
            dim = sudoku.Dimensions(root)
            self.assertEqual(root, dim.root)
            self.assertEqual(root**2, dim.size)

    def test_get_int_in_range(self):
        dim = sudoku.Dimensions(3)
        
        self.assertRaises(sudoku.OutOfRangeException, dim.get_int_in_range, 11)
        self.assertRaises(sudoku.OutOfRangeException, dim.get_int_in_range, -1)
        self.assertRaises(sudoku.OutOfRangeException, dim.get_int_in_range, 'Not an integer')
        for i in dim.all_moves:
            i_int = dim.get_int_in_range(i)
        
        
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
        self.assertRaises(sudoku.OutOfRangeException, self.cell.move, 'Invalid move - nonnumber')
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
        
        
    def test_deny_move(self):
        self.cell.deny_move(5)
        self.assertFalse(self.cell.is_allowed_move(5), msg='Move should be denied')



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
                

class CellGroupMixin(object):
    
    def init(self, dims=3):
        self.dims = sudoku.Dimensions(dims)


    def buildEmptyGroup(self):
        return sudoku.CellGroup(self.dims)
        
        
    def buildGroup(self):
        group = self.buildEmptyGroup()
        for i in self.dims.all_moves:
            group.add_cell(sudoku.Cell(self.dims))
        return group
        
            

class TestCellGroup(unittest.TestCase, CellGroupMixin):

    def setUp(self):
        self.init(3)
    
    def test_empty_group(self):
        group = self.buildEmptyGroup()
        self.assertEqual(len(group.cells), 0)
        
        
    def test_group_dimensions(self):
        group = self.buildGroup()
        self.assertEqual(len(group.cells), self.dims.size)
        self.assertRaises(IndexError, group.add_cell, sudoku.Cell(self.dims))
        
        
    def test_bad_cell(self):
        group = self.buildEmptyGroup()
        group.add_cell(sudoku.Cell(self.dims))
        self.assertRaises(Exception, group.add_cell, 'This is not a cell')

        
    def test_cell_moves(self):
        group = self.buildGroup()
        
        group.cell(1).move(5)
        self.assertEqual(group.cells[0].value, 5)
        
        group.cell(9).move(6)
        self.assertEqual(group.cells[8].value, 6)
        
        self.assertRaises(sudoku.DeniedMoveException, group.cell(4).move, 6)

        

class TestBoard(unittest.TestCase):
    
    def setUp(self):
        self.board = sudoku.Board(3, [sudoku.BaseSolver()])

        
    def check_row_col_square(self, cell_global_index, row, col, square, cell_square_index, value):
        cell = self.board.cell(cell_global_index)
        self.assertEquals(cell.row, row)
        self.assertEquals(cell.col, col)
        self.assertEquals(cell.square, square)
        cell.move(value)
        self.assertEqual(value, self.board.row(row).cell(col).value)
        self.assertEqual(value, self.board.col(col).cell(row).value)
        sq = self.board.square(square)
        self.assertEqual(value, sq.cell(cell_square_index).value)
        self.assertIn(cell.row, sq.rows)
        self.assertIn(cell.col, sq.cols)
        
        
    def test_init(self):
        self.assertEqual(len(self.board.cells), 81)
        self.assertEqual(len(self.board.rows), 9)
        self.assertEqual(len(self.board.cols), 9)
        self.assertEqual(len(self.board.squares), 9) 
        for sq_row in (0, 1, 2):
            for sq_col in (0, 1, 2):
                sq_idx = sq_row * 3 + sq_col + 1
                square = self.board.square(sq_idx)
                self.assertEquals(square.rows, [1 + 3 * sq_row, 2 + 3 * sq_row, 3 + 3 * sq_row])
                self.assertEquals(square.cols, [1 + 3 * sq_col, 2 + 3 * sq_col, 3 + 3 * sq_col])
        for cell in self.board.cells:
            self.assertEqual(0, cell.value)
            
            
    def test_rows_cols_squares(self):
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
        
        
    def test_moves(self):
        self.assertEquals(self.board.moves, [])
        self.board.row(1).cell(3).move(4)
        self.assertEquals(self.board.moves, [(1, 3, 4)])
        self.board.col(2).cell(3).move(1)
        self.assertEquals(self.board.moves, [(1, 3, 4), (3, 2, 1)])
        self.board.square(8).cell(4).move(9)
        self.assertEquals(self.board.moves, [(1, 3, 4), (3, 2, 1), (8, 4, 9)])
        self.board.move([(1, 4, 5)])
        self.assertEquals(self.board.moves, [(1, 3, 4), (3, 2, 1), (8, 4, 9), (1, 4, 5)])
        self.board.move([(9, 7, 3), (9, 8, 5)])
        self.assertEquals(self.board.moves, [(1, 3, 4), (3, 2, 1), (8, 4, 9), (1, 4, 5), (9, 7, 3), (9, 8, 5)])
        


class TestBaseSolver(unittest.TestCase, CellGroupMixin):
    
    def setUp(self):
        self.init(3)
        self.board = sudoku.Board(3, [sudoku.BaseSolver()])
        
    
    def test_board_solver(self):
        
        for i in range(1, 9):
            self.board.row(1).cell(i).move(i)
        (cell, value) = self.board.find_move()
        self.assertEqual(9, value)
        self.assertEqual(cell, self.board.cell(9))
        
        
    def test_board_solver2(self):

        # cell 1..6 => value 1..6
        for i in range(1, 7):
            self.board.row(1).cell(i).move(i)
        self.board.row(4).cell(7).move(8)
        self.board.row(8).cell(9).move(8)
        (cell, value) = self.board.find_move()
        self.assertEqual(8, value)
        self.assertEqual(cell, self.board.row(1).cell(8))
        
        # Test undo
        cell.move(8)
        cell.empty()
        (cell, value) = self.board.find_move()
        self.assertEqual(8, value)
        self.assertEqual(cell, self.board.row(1).cell(8))
        (cell, value) = self.board.find_move()
        self.assertEqual(8, value)
        self.assertEqual(cell, self.board.row(1).cell(8))
        
        
    def test_group_solver(self):
        group = self.buildGroup()
        solver = sudoku.BaseSolver()
        
        for i in range(1, 9):
            group.cell(i).move(i)
            
        (cell, value) = solver.find_move(group)
        
        self.assertEqual(9, value)
        self.assertEqual(cell, group.cell(9))
        
        
    def test_group_solver_2(self):
        group = self.buildGroup()
        solver = sudoku.BaseSolver()

        # cell 1..6 => value 1..6
        for i in range(1, 7):
            group.cell(i).move(i)
            
        group.cell(7).deny_move(8)
        group.cell(9).deny_move(8)
        
        (cell, value) = solver.find_move(group)
        
        self.assertEqual(8, value)
        self.assertEqual(cell, group.cell(8))
        

    def test_board_solver3(self):
        for r, c, m in ((1, 1, 1), (4, 3, 1), (7, 4, 1), (9, 9, 1)):
            self.board.row(r).cell(c).move(m)
        self.assertIn(1, self.board.square(7).allowed_moves())
        self.assertIn(1, self.board.row(8).cell(2).allowed_moves())
        self.assertNotIn(1, self.board.row(8).cell(1).allowed_moves())
        self.assertNotIn(1, self.board.row(8).cell(3).allowed_moves())
        for row in (7, 9):
            for col in (1, 2, 3):
                self.assertNotIn(1, self.board.row(row).cell(col).allowed_moves())
        (cell, value) = self.board.find_move()
        self.assertEqual(1, value)
        self.assertEqual(cell, self.board.row(8).cell(2))
 
 
 
 
if __name__ == '__main__':
    unittest.main()


