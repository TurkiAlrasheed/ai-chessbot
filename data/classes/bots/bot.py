import copy
import random

class Bot:
    """
    A bot that makes random moves.
    """
    def __init__(self):
        pass
        
    def get_possible_moves(self, side, board):
        return board.get_all_valid_moves(side)
    
    def evaluate_board(self, side, board):
        return
    
    def simulate_move(self, board, start_pos, end_pos):
        new_board = copy.deepcopy(board)
        new_board.handle_move(start_pos, end_pos)
        return new_board
    
    def ab_minimax(self, board, side, depth, a, b, maximizing_player):
        if depth == 0 or board.is_in_checkmate(side):
            return self.evaluate_board(side, board)

        moves = board.get_all_valid_moves(side)
        if maximizing_player:
            max_eval = float('-inf')
            for init_pos, end_pos in moves:
                simulated_board = self.simulate_move(board, init_pos, end_pos)
                eval = self.ab_minimax(simulated_board, side, depth - 1, False)
                max_eval = max(max_eval, eval)
                a = max(max_eval, eval)
                if b <= a:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for init_pos, end_pos in moves:
                simulated_board = self.simulate_move(board, init_pos, end_pos)
                eval = self.ab_minimax(simulated_board, side, depth - 1, True)
                min_eval = min(min_eval, eval)
                b = min(min_eval, eval)
                if b <= a:
                    break
            return min_eval

    def move(self, side, board):
        return