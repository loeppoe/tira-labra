import math
import time

EMPTY = 0
PLAYER = 1
OPPONENT = 2
BOARD_SIZE = 19
WINNING_LENGTH = 5
SEARCH_RADIUS = 2

def create_board():
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def print_board(board):
    for row in board:
        print(' '.join(['.' if cell == EMPTY else 'X' if cell == PLAYER else 'O' for cell in row]))

def is_winning_move(board, player):
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if check_line(board, player, i, j, 1, 0) or \
               check_line(board, player, i, j, 0, 1) or \
               check_line(board, player, i, j, 1, 1) or \
               check_line(board, player, i, j, 1, -1):
                return True
    return False

def check_line(board, player, row, col, d_row, d_col):
    count = 0
    for _ in range(WINNING_LENGTH):
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE and board[row][col] == player:
            count += 1
            if count == WINNING_LENGTH:
                return True
        else:
            break
        row += d_row
        col += d_col
    return False

def evaluate_board(board):
    score = 0
    score += score_lines(board, PLAYER)
    score -= score_lines(board, OPPONENT)
    return score

def score_lines(board, player):
    score = 0
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            score += evaluate_line(board, player, i, j, 1, 0)  # Horizontal
            score += evaluate_line(board, player, i, j, 0, 1)  # Vertical
            score += evaluate_line(board, player, i, j, 1, 1)  # Diagonal down-right
            score += evaluate_line(board, player, i, j, 1, -1)  # Diagonal up-right
    return score

def evaluate_line(board, player, row, col, d_row, d_col):
    line = []
    for _ in range(WINNING_LENGTH + 2):
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            line.append(board[row][col])
        else:
            line.append(None)
        row += d_row
        col += d_col
    return evaluate_pattern(line, player)

def evaluate_pattern(line, player):
    opponent = OPPONENT if player == PLAYER else PLAYER
    patterns = [
        (50, [EMPTY, player, player, player, player, EMPTY]),  # Live four
        (10, [EMPTY, player, player, player, player]),         # Dead four
        (10, [EMPTY, player, player, player, EMPTY, EMPTY]),   # Live three
        (10, [EMPTY, EMPTY, player, player, player, EMPTY]),   # Live three
        (5, [EMPTY, player, player, player, EMPTY]),           # Dead three
        (5, [EMPTY, player, player, EMPTY, player]),           # Dead three
        (5, [player, EMPTY, player, player, EMPTY]),           # Dead three
        (5, [player, player, EMPTY, player, EMPTY])            # Dead three
    ]
    
    score = 0
    for value, pattern in patterns:
        if matches_pattern(line, pattern):
            score += value

    opponent_patterns = [
        (40, [EMPTY, opponent, opponent, opponent, opponent, EMPTY]),  # Live four (opponent)
        (8, [EMPTY, opponent, opponent, opponent, opponent]),         # Dead four (opponent)
        (8, [EMPTY, opponent, opponent, opponent, EMPTY, EMPTY]),     # Live three (opponent)
        (8, [EMPTY, EMPTY, opponent, opponent, opponent, EMPTY]),     # Live three (opponent)
        (4, [EMPTY, opponent, opponent, opponent, EMPTY]),            # Dead three (opponent)
        (4, [EMPTY, opponent, opponent, EMPTY, opponent]),            # Dead three (opponent)
        (4, [opponent, EMPTY, opponent, opponent, EMPTY]),            # Dead three (opponent)
        (4, [opponent, opponent, EMPTY, opponent, EMPTY])             # Dead three (opponent)
    ]

    for value, pattern in opponent_patterns:
        if matches_pattern(line, pattern):
            score -= value

    return score

def matches_pattern(line, pattern):
    for i in range(len(line) - len(pattern) + 1):
        match = True
        for j in range(len(pattern)):
            if pattern[j] is not None and line[i + j] != pattern[j]:
                match = False
                break
        if match:
            return True
    return False

def minimax(board, depth, alpha, beta, maximizingPlayer, last_move):
    if depth == 0 or is_winning_move(board, PLAYER) or is_winning_move(board, OPPONENT):
        return evaluate_board(board)

    if maximizingPlayer:
        maxEval = -math.inf
        for move in generate_moves(board, last_move):
            board[move[0]][move[1]] = PLAYER
            eval = minimax(board, depth - 1, alpha, beta, False, move)
            board[move[0]][move[1]] = EMPTY
            maxEval = max(maxEval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return maxEval
    else:
        minEval = math.inf
        for move in generate_moves(board, last_move):
            board[move[0]][move[1]] = OPPONENT
            eval = minimax(board, depth - 1, alpha, beta, True, move)
            board[move[0]][move[1]] = EMPTY
            minEval = min(minEval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return minEval

def generate_moves(board, last_move):
    moves = []
    if last_move is None:
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if board[i][j] == EMPTY:
                    moves.append((i, j))
    else:
        row_start = max(0, last_move[0] - SEARCH_RADIUS)
        row_end = min(BOARD_SIZE, last_move[0] + SEARCH_RADIUS + 1)
        col_start = max(0, last_move[1] - SEARCH_RADIUS)
        col_end = min(BOARD_SIZE, last_move[1] + SEARCH_RADIUS + 1)

        for i in range(row_start, row_end):
            for j in range(col_start, col_end):
                if board[i][j] == EMPTY:
                    moves.append((i, j))
    return moves

def get_best_move(board, last_move, first_move=False):
    if first_move:
        center = BOARD_SIZE // 2
        if board[center][center] == EMPTY:
            return center, center

    best_move = None
    best_value = -math.inf
    for move in generate_moves(board, last_move):
        board[move[0]][move[1]] = PLAYER
        move_value = minimax(board, 2, -math.inf, math.inf, False, move)  # Reduced depth for speed
        board[move[0]][move[1]] = EMPTY
        if move_value > best_value:
            best_value = move_value
            best_move = move
    return best_move

def play_game():
    board = create_board()
    print_board(board)
    
    ai_first_move = True
    last_move = None

    print("AI is making the first move...")
    start_time = time.time()
    best_move = get_best_move(board, last_move, first_move=ai_first_move)
    ai_first_move = False
    if best_move is not None:
        board[best_move[0]][best_move[1]] = PLAYER
        last_move = best_move
        print_board(board)
        if is_winning_move(board, PLAYER):
            print("AI wins!")
            return
    else:
        print("Draw!")
        return
    print(f"AI move took {time.time() - start_time:.2f} seconds")

    while True:
        row = int(input("Enter row: "))
        col = int(input("Enter col: "))
        if board[row][col] == EMPTY:
            board[row][col] = OPPONENT
            last_move = (row, col)
        else:
            print("Invalid move! Try again.")
            continue

        print_board(board)
        if is_winning_move(board, OPPONENT):
            print("Opponent wins!")
            break

        print("AI is making a move...")
        start_time = time.time()
        best_move = get_best_move(board, last_move)
        if best_move is not None:
            board[best_move[0]][best_move[1]] = PLAYER
            last_move = best_move
            print_board(board)
            if is_winning_move(board, PLAYER):
                print("AI wins!")
                break
        else:
            print("Draw!")
            break
        print(f"AI move took {time.time() - start_time:.2f} seconds")

play_game()