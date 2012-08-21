import sudoku
import unittest

class TestCell(unittest.TestCase):

    def setUp(self):
        self.cell = sudoku.Cell()
        
        
    def test_move(self):
        self.cell.move(5)
        self.assertEqual(self.cell.value(), 5)

        # should raise an exception for illegal or out of range values
        self.assertRaises(ValueError, self.cell.move, 'Invalid move')
        self.assertRaises(ValueError, self.cell.move, -1)
        self.assertRaises(ValueError, self.cell.move, sudoku.DIMENSIONS + 1)
        
        
    def test_clean(self):
        self.cell.move(5)
        self.assertFalse(self.cell.is_clean())
        
        self.cell.clean()
        self.assertTrue(self.cell.is_clean())
        self.assertEqual(self.cell.value(), 0)
        
        
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
    
    def buildEmptyGroup(self):
        return sudoku.CellGroup()
        
        
    def buildGroup(self):
        group = self.buildEmptyGroup()
        for i in range(sudoku.DIMENSIONS):
            group.add_cell(sudoku.Cell())
        return group
        
            
    def test_empty_group(self):
        group = self.buildEmptyGroup()
        self.assertEqual(len(group._cells), 0)
        
        
    def test_group_dimensions(self):
        group = self.buildGroup()
        self.assertEqual(len(group._cells), sudoku.DIMENSIONS)
        self.assertRaises(IndexError, group.add_cell, sudoku.Cell())
        
        
    def test_bad_cell(self):
        group = self.buildEmptyGroup()
        group.add_cell(sudoku.Cell())
        self.assertRaises(Exception, group.add_cell, 'This is not a cell')

        
    def test_two_groups(self):
        g1 = self.buildGroup()
        g2 = self.buildGroup()
        
        g1.move(1, 5)
        self.assertEqual(g1._cells[0].value(), 5)
        
        g2.move(9, 5)
        self.assertEqual(g2._cells[8].value(), 5)
        
        g1.move(1, 5)
        g2.move(1, 3)
        self.assertNotEqual(g1._cells[0].value(), g2._cells[0].value())
        
    
if __name__ == '__main__':
    unittest.main()


