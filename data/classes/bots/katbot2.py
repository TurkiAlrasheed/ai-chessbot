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
    


class Bot:
    """
    A bot that bots.
    """
    def __init__(self):
        self.depth = 3
        self.time_limit_ms = 100  # 0.1 second in milliseconds
        self.start_time_ms = None
        #self.position_history = {}

    def opponent(self, side):
        return 'black' if side == 'white' else 'white'
    
    '''
    def hash_board_state(self, board):
        # Flatten the 6x6 board into a string and return a hash
        flat = tuple(tuple(row) for row in board.get_board_state())
        return hash(flat)
    '''   
    
    def get_possible_moves(self, side, board):
        return board.get_all_valid_moves(side)

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
        my_king_position = None
        opponent_pieces = []
        my_pieces = []

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
                    if type_char == "K":  # Track king position for safety evaluation
                        my_king_position = (row, col)
                    my_pieces.append((type_char, row, col))
                elif color == 'b':
                    evaluation += score if side == 'black' else -score
                    opponent_pieces.append((type_char, row, col))

        # King Safety: Bonus for defended king, penalty for exposed king
        if my_king_position:
            king_row, king_col = my_king_position
            defense_count = 0
            for r in range(king_row - 1, king_row + 2):
                for c in range(king_col - 1, king_col + 2):
                    if 0 <= r < 6 and 0 <= c < 6:
                        piece = board_state[r][c]
                        if piece != "" and piece[0] == side[0]:  # Friendly piece
                            defense_count += 1
            evaluation += defense_count * 0.5  # Defended king is more valuable

        # Piece Safety: Penalize pieces that are under threat
        for piece, row, col in my_pieces:
            is_safe = True
            for r in range(row - 1, row + 2):
                for c in range(col - 1, col + 2):
                    if 0 <= r < 6 and 0 <= c < 6:
                        opponent_piece = board_state[r][c]
                        if opponent_piece != "" and opponent_piece[0] == self.opponent(side)[0]:
                            is_safe = False
            if not is_safe:
                evaluation -= 2  # Penalize unsafe pieces

        # Mobility bonus
        my_moves = len(board.get_all_valid_moves(side))
        opp_moves = len(board.get_all_valid_moves(self.opponent(side)))
        evaluation += 0.1 * (my_moves - opp_moves)

        # Pawn promotion potential
        for row in range(6):
            for col in range(6):
                piece = board_state[row][col]
                if piece == "":
                    continue
                color, type_char = piece[0], piece[1]
                if type_char == " " and color == side[0]:  # Only check pawns
                    # Assign higher value to pawns nearing promotion
                    if side == 'white' and row > 2:
                        evaluation += (6 - row) * 0.5
                    elif side == 'black' and row < 3:
                        evaluation += (3 - row) * 0.5

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

        '''
        simulated_board = self.simulate_move(board, best_move[0], best_move[1])
        state_hash = self.hash_board_state(simulated_board)
        self.position_history[state_hash] = self.position_history.get(state_hash, 0) + 1
        '''
        
        return best_move


    