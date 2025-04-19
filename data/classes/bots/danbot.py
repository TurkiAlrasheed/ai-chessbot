import copy
import random
import pygame
def deepcopy_ignore_surfaces(obj, memo=None):
    if memo is None:
        memo = {}

    if id(obj) in memo:
        return memo[id(obj)]

    if isinstance(obj, pygame.Surface):
        return obj

    if isinstance(obj, dict):
        copied = {}
        memo[id(obj)] = copied
        for k, v in obj.items():
            copied[deepcopy_ignore_surfaces(k, memo)] = deepcopy_ignore_surfaces(v, memo)
        return copied

    elif isinstance(obj, list):
        copied = []
        memo[id(obj)] = copied
        for item in obj:
            copied.append(deepcopy_ignore_surfaces(item, memo))
        return copied

    elif hasattr(obj, '__dict__'):
        copied = obj.__class__.__new__(obj.__class__)
        memo[id(obj)] = copied
        for k, v in obj.__dict__.items():
            setattr(copied, k, deepcopy_ignore_surfaces(v, memo))
        return copied

    else:
        return copy.deepcopy(obj, memo)
    
PIECE_SQUARE_TABLES = {
    " ": [  # Pawn
        [6,   6,   6,   6,   6,   6],
        [5,   5,   5,   5,   5,   5],
        [1,   1,   2,   2,   1,   1],
        [0.5, 0.5, 1,   1,   0.5, 0.5],
        [0,   0,   0.5, 0.5, 0,   0],
        [0,   0,   0,   0,   0,   0]
    ],
    "N": [  # Knight
        [-2, -1, -1, -1, -1, -2],
        [-1,  0,  0.5, 0.5, 0, -1],
        [-1,  0.5, 1, 1, 0.5, -1],
        [-1,  0.5, 1, 1, 0.5, -1],
        [-1,  0,  0.5, 0.5, 0, -1],
        [-2, -1, -1, -1, -1, -2]
    ],
    # You can later add "B", "R", "S", "Q", "J", "K"
    "B": [  # Bishop
        [-2, -1, -1, -1, -1, -2],
        [-1,  0,  0.5, 0.5, 0, -1],
        [-1,  0.5, 1, 1, 0.5, -1],
        [-1,  0.5, 1, 1, 0.5, -1],
        [-1,  0,  0.5, 0.5, 0, -1],
        [-2, -1, -1, -1, -1, -2]
    ],
    "R": [  # Rook
        [1,   1,   2,   2,   1,   1],
        [0.5, 1,   1,   1,   1,   0.5],
        [0,  0,  0.5, 0.5, 0, 0],
        [-1,  -0.5, -1, -1, -0.5, -1],
        [-1,  -0.5, -1, -1, -0.5, -1],
        [-1.5,   -1.5, -1.5, -1.5, -1.5, -5]
    ],
    "Q": [
        [1,   1,   2,   2,   1,   1],
        [0.5, 1,   1,   1,   1,   0.5],
        [0,  0,  0.5, 0.5, 0, 0],
        [5,  5, 5, 5, 5, -5],
        [-1,  -0.5, -1, -1, -0.5, -1],
        [-1.5,   -1.5, -1.5, -1.5, -1.5, -5]
    ],
    "S": [
        [1,   1,   2,   2,   1,   1],
        [0.5, 1,   1,   1,   1,   0.5],
        [0,  0,  0.5, 0.5, 0, 0],
        [5,  5, 5, 5, 5, -5],
        [-1,  -0.5, -1, -1, -0.5, -1],
        [-1.5,   -1.5, -1.5, -1.5, -1.5, -5]
    ],
    "J": [
        [1,   1,   2,   2,   1,   1],
        [0.5, 1,   1,   1,   1,   0.5],
        [0,  0,  0.5, 0.5, 0, 0],
        [5,  5, 5, 5, 5, -5],
        [-1,  -0.5, -1, -1, -0.5, -1],
        [-1.5,   -1.5, -1.5, -1.5, -1.5, -5]
    ],
    "K": [
        [-5,   -5,   -5,   -5,   -5,   -5],
        [-5,   -5,   -5,   -5,   -5,   -5],
        [-5,   -5,   -5,   -5,   -5,   -5],
        [-2,   -2,   -2,   -2,   -2,   -2],
        [-1.5,   -1.5, -1.5, -1.5, -1.5, -5],
        [0, 0, 0, 0, 0, 0]
    ]
   

}

class Bot:
    def __init__(self):
        self.depth = 2
        
    def get_possible_moves(self, side, board):
        return board.get_all_valid_moves(side)
    
    
    def evaluate_board(self, side, board):
        SCORES_DICT = {
            " ": 10,   # pawn
            "N": 30,   # knight
            "B": 30,   # bishop
            "R": 50,   # rook
            "S": 50,   # star
            "Q": 90,   # queen
            "J": 90,   # joker
            "K": 10000  # king
        }

        board_state = board.get_board_state()
        evaluation = 0
        side_prefix = 'w' if side == 'white' else 'b'
        opponent_prefix = 'b' if side == 'white' else 'w'
        king_pos = None

        for row in range(6):
            for col in range(6):
                piece = board_state[row][col]
                if piece == "":
                    continue

                color, piece_type = piece[0], piece[1]
                value = SCORES_DICT.get(piece_type, 0)

                # Apply positional bonus from PST if available
                if piece_type in PIECE_SQUARE_TABLES:
                    pst = PIECE_SQUARE_TABLES[piece_type]
                    table_row = row if color == 'w' else 5 - row  # flip for black
                    positional_bonus = pst[table_row][col]
                    value += positional_bonus

                if color == side_prefix:
                    evaluation += value
                    if piece_type == "K":
                        king_pos = (row, col)
                else:
                    evaluation -= value

        # King safety (friendly pieces near king)
        if king_pos:
            def count_friendly_near_king(pos, board_state, prefix):
                count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        r, c = pos[0] + dr, pos[1] + dc
                        if 0 <= r < 6 and 0 <= c < 6:
                            p = board_state[r][c]
                            if p != "" and p[0] == prefix:
                                count += 1
                return count

            guards = count_friendly_near_king(king_pos, board_state, side_prefix)
            evaluation += guards * 5  # Tune this value

        return evaluation

    
    def ab_minimax(self, board, side, depth, a, b, maximizing_player):
        if depth == 0 or board.is_in_checkmate(side):
            return self.evaluate_board(side, board)

        moves = board.get_all_valid_moves(side)
        if maximizing_player:
            max_eval = float('-inf')
            for init_pos, end_pos in moves:
                simulated_board = self.simulate_move(board, init_pos, end_pos)
                eval = self.ab_minimax(simulated_board, side, depth - 1, a, b, False)
                max_eval = max(max_eval, eval)
                a = max(a, eval)
                if b <= a:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for init_pos, end_pos in moves:
                simulated_board = self.simulate_move(board, init_pos, end_pos)
                eval = self.ab_minimax(simulated_board, side, depth - 1, a, b, True)
                min_eval = min(min_eval, eval)
                b = min(b, eval)
                if b <= a:
                    break
            return min_eval

    def get_best_move_minimax(self, board, side, depth):
        best_move = []
        best_value = float('-inf')
        moves = board.get_all_valid_moves(side)
        for init_pos, end_pos in moves:
            simulated_board = self.simulate_move(board, init_pos, end_pos)
            move_value = self.ab_minimax(simulated_board, side, depth - 1, float('-inf'), float('inf'), False)
            if move_value > best_value:
                best_value = move_value
                best_move = [(init_pos, end_pos)]
            elif move_value == best_value:
                best_move.append((init_pos, end_pos))
        return best_move[0] if len(best_move) == 1 else random.choice(best_move)
        
    def move(self, side, board):
        best_move = self.get_best_move_minimax(board, side, self.depth)
        return best_move
    

    def simulate_move(self, board, start_pos, end_pos):
        new_board = deepcopy_ignore_surfaces(board)
        new_board.handle_move(start_pos, end_pos)
        return new_board

    