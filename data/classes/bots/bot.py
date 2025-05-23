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
        self.depth = 3
        self.time_limit_ms = 100  # 0.1 second in milliseconds
        self.start_time_ms = None

    def opponent(self, side):
        return 'black' if side == 'white' else 'white'
        
    def get_possible_moves(self, side, board):
        return board.get_all_valid_moves(side)
    
    '''
    def evaluate_board(self, side, board):
        SCORES_DICT = {
            " ": 1,  # pawn
            "N": 3,  # knight
            "B": 3,  # bishop
            "R": 5,  # rook
            "S": 5,  # star
            "Q": 9,  # queen
            "J": 9,  # joker
            "K": 100  # king
        }

        POSITION_BONUS = [
            [0, 1, 2, 2, 1, 0],
            [1, 2, 3, 3, 2, 1],
            [2, 3, 4, 4, 3, 2],
            [2, 3, 4, 4, 3, 2],
            [1, 2, 3, 3, 2, 1],
            [0, 1, 2, 2, 1, 0],
        ]

        evaluation = 0
        board_state = board.get_board_state()

        for row in range(6):
            for col in range(6):
                piece = board_state[row][col]
                if piece == "":
                    continue

                color, type_char = piece[0], piece[1]
                value = SCORES_DICT.get(type_char, 0)
                bonus = POSITION_BONUS[row][col]

                # Apply score based on side
                score = value + 0.2 * bonus  # Slightly higher bonus scaling for tighter board
                if color == 'w':
                    evaluation += score if side == 'white' else -score
                elif color == 'b':
                    evaluation += score if side == 'black' else -score

        # Mobility bonus
        my_moves = len(board.get_all_valid_moves(side))
        opp_moves = len(board.get_all_valid_moves(self.opponent(side)))
        evaluation += 0.1 * (my_moves - opp_moves)

        return evaluation
    '''

    def evaluate_board(self, side, board):
        SCORES_DICT = {
            " ": 1,  # pawn
            "N": 3,  # knight
            "B": 3,  # bishop
            "R": 5,  # rook
            "S": 5,  # star
            "Q": 9,  # queen
            "J": 9,  # joker
            "K": 100  # king
        }

        POSITION_BONUS = [
            [0, 1, 2, 2, 1, 0],
            [1, 2, 3, 3, 2, 1],
            [2, 3, 4, 4, 3, 2],
            [2, 3, 4, 4, 3, 2],
            [1, 2, 3, 3, 2, 1],
            [0, 1, 2, 2, 1, 0],
        ]

        evaluation = 0
        board_state = board.get_board_state()

        for row in range(6):
            for col in range(6):
                piece = board_state[row][col]
                if piece == "":
                    continue

                color, type_char = piece[0], piece[1]
                value = SCORES_DICT.get(type_char, 0)
                bonus = POSITION_BONUS[row][col]

                # Apply score based on side
                score = value + 0.2 * bonus  # Slightly higher bonus scaling for tighter board
                if color == 'w':
                    evaluation += score if side == 'white' else -score
                elif color == 'b':
                    evaluation += score if side == 'black' else -score

        # Mobility bonus
        my_moves = len(board.get_all_valid_moves(side))
        opp_moves = len(board.get_all_valid_moves(self.opponent(side)))
        evaluation += 0.1 * (my_moves - opp_moves)

        return evaluation

    def simulate_move(self, board, start_pos, end_pos):
        new_board = deepcopy_ignore_surfaces(board)
        new_board.handle_move(start_pos, end_pos)
        return new_board
    
    def ab_minimax(self, board, side, depth, a, b, maximizing_player):
        if pygame.time.get_ticks() - self.start_time_ms >= self.time_limit_ms:
            print('timed out')
            return self.evaluate_board(side, board)

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
        self.start_time_ms = pygame.time.get_ticks()
        best_move = self.get_best_move_minimax(board, side, self.depth)
        return best_move


    