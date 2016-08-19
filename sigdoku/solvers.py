# -*- coding: utf-8 -*-

        
class BaseSolver(object):
    """
    Implements the find_move method which is based solely on cell constraints;
    more advanced solvers should override reduce_allowed_moves
    This solver should always be first in the Board.solvers list
    """
    
    def find_move(self, board, allowed_moves):        
        self.reduce_allowed_moves(board, allowed_moves)
        
        for c in board.cells:
            cam = allowed_moves[c] if not c.value else []
            if len(cam) == 1:
                return (c, list(cam)[0])
                
        for group in board.all_groups:
            for value in group.allowed_moves():
                cell = None
                for c in group.cells:
                    if not c.value and value in allowed_moves[c]:
                        if cell is None:
                            cell = c
                        else:
                            cell = None
                            break
                if not cell is None:
                    return (cell, value)
                    
        return (None, None)
        
        
    def reduce_allowed_moves(self, board, allowed_moves):
        pass
        


class RowColInSquareSolver(BaseSolver):
    """
    If a move is allowed only within a row or col of a square,
    remove it from the same row/col in the other squares
    """
    
    def reduce_allowed_moves(self, board, allowed_moves):
        for square in board.squares:
            for value in square.allowed_moves():
                rc = [(cell.row, cell.col) for cell in square.cells if not cell.value and value in allowed_moves[cell]]
                if len(rc):
                    rows, cols = [list(set(a)) for a in zip(*rc)]
                    if len(rows) == 1:
                        self.__deny_rowcol(value, board.row(rows[0]), square.index, allowed_moves)
                    elif len(cols) == 1:
                        self.__deny_rowcol(value, board.col(cols[0]), square.index, allowed_moves)


    def __deny_rowcol(self, value, group, square_idx, allowed_moves):
        for cell in group.cells:
            if (not cell.value) and (cell.square != square_idx) and (value in allowed_moves[cell]):
                allowed_moves[cell].remove(value)



class CoupleTripletInGroupSolver(BaseSolver):
    """
    If two moves are the only possible moves for two cells of the same group, 
    or three moves are the only possible moves for three cells, 
    remove them from the other cells of the group
    """
    
    def reduce_allowed_moves(self, board, allowed_moves):
        for group in board.all_groups:
            gmoves = {}
            for cell in group.cells:
                if not cell.value:
                    am = frozenset(allowed_moves[cell])
                    if len(am) > 1 and len(am) <= board.dimensions.root:
                        l = gmoves.get(am, list())
                        l.append(cell)
                        gmoves[am] = l
            for am, cells in gmoves.items():
                if len(cells) == len(am):
#                    print "%s => %s" % (am, '|'.join(['(%d %d %d)' % (c.row, c.col, c.value) for c in cells]))
                    for cell in group.cells:
                        if not cell.value and not cell in cells:
                            for v in list(allowed_moves[cell]):
                                if v in am:
                                    allowed_moves[cell].remove(v)
        
       
