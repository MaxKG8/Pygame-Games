import numpy as np
import random
import pygame
import sys
import math

BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

ROW_COUNT = 6
COLUMN_COUNT = 7

# Whos turn is it
PLAYER = 0
AI = 1

# Number corresponding to color
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4

def create_board():
	board = np.zeros((ROW_COUNT,COLUMN_COUNT))
	return board

def drop_piece(board, row, col, piece):
	board[row][col] = piece

def is_valid_location(board, col):
	return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
	for r in range(ROW_COUNT):
		if board[r][col] == 0:
			return r

def print_board(board):
	print(np.flip(board, 0))

def winning_move(board, piece):
	# Check horizontal locations for win
	for c in range(COLUMN_COUNT-3):
		for r in range(ROW_COUNT):
			if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
				return True

	# Check vertical locations for win
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT-3):
			if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
				return True

	# Check positively sloped diaganols
	for c in range(COLUMN_COUNT-3):
		for r in range(ROW_COUNT-3):
			if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
				return True

	# Check negatively sloped diaganols
	for c in range(COLUMN_COUNT-3):
		for r in range(3, ROW_COUNT):
			if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
				return True


def eval_window(window, piece):
	score = 0

	opp_piece = PLAYER_PIECE
	if piece == PLAYER_PIECE:
		opp_piece = AI_PIECE

	# If piece in given position would make it 4 in a row, AI gotta drop there.
	# drop in front of own AI piece to win game or player piece to stop them from winning
	if window.count(piece) == 4:
		score += 100
	elif window.count(piece) == 3 and window.count(EMPTY) == 1:
		score += 5
	elif window.count(piece) == 2 and window.count(EMPTY) == 2:
		score += 2

	# Blocks if player getting 4 in a row
	if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
		score -= 4

	return score


def score_position(board, piece):

	score = 0

	# Score center column
	# [:, COLUMN_COUNT//2] will give us center column (// is floor division)
	center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
	center_count = center_array.count(piece)
	score += center_count * 3


	# Score Horizontal
	# For every row on board you must check the first 4 columns
	for r in range(ROW_COUNT):
		row_array = [int(i) for i in list(board[r,:])]

		# Using -3 cuz later u are 4 pieces after the starting piece which will finaly be the 4th, 4+3=7
		for c in range(COLUMN_COUNT-3):
			window = row_array[c : c+WINDOW_LENGTH]
			score += eval_window(window, piece)

	# Score Vertical
	for c in range(COLUMN_COUNT):
		col_array = [int(i) for i in list(board[:,c])]
		# Using -3 cuz later u are 4 pieces after the starting piece which will finaly be the 4th, 4+3=7
		for r in range(ROW_COUNT-3):
			window = col_array[r:r+WINDOW_LENGTH]
			score += eval_window(window, piece)

	# Score Positive Slope Diagonal
	# Window list start point iterates thru 4 rows
	for r in range(ROW_COUNT-3):
		# For every row, window list start point iterates thru 4 of the columns
		for c in range(COLUMN_COUNT-3):
			# Gets array of positively diagonal pieces for one of the many starting points iterating in the above loop
			window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
			score += eval_window(window, piece)

	# Score Negative Slope Diagonal
	for r in range(ROW_COUNT-3):
		for c in range(COLUMN_COUNT-3):
			window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)] # WINDOW_LENGTH = 4
			score += eval_window(window, piece)

	# Score Negative Slope Diagonal

	return score


def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0
    

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else: # Game is over, no more valid moves
                return (None, 0)
        else: # Depth is 0
            return (None, score_position(board, AI_PIECE))

    if maximizingPlayer: # AI
        value = -math.inf
        # Random initialization
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            # maximizingPlayer == False so 
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col

            alpha = max(alpha, value)
            if alpha >= beta:
                break

        return column, value


    else: # Minimizing player / HUMAN PLAYER
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col

            beta = min(beta, value)
            if alpha >= beta:
                break

        return column, value



# valid_locations is a LIST
# get_valid_location is a FUNCTION
# is_valid_location is a FUNCITON

def get_valid_locations(board):
	valid_locations = []
	for col in range(COLUMN_COUNT):
		if is_valid_location(board, col):
			valid_locations.append(col)
	return valid_locations

def pick_best_move(board, piece):
	valid_locations = get_valid_locations(board)
	best_score = -10000
	# Will drop randomly unless there is opportunity to get 3 or 4 in a row
	best_col = random.choice(valid_locations)

	for col in valid_locations:
		row = get_next_open_row(board, col)
		temp_board = board.copy()
		drop_piece(temp_board, row, col, piece)
		score = score_position(temp_board, piece)
		
		if score > best_score:
			best_score = score
			best_col = col
		
	return best_col


def draw_board(board):
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):
			pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
			pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
	
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):		
			if board[r][c] == PLAYER_PIECE:
				pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
			elif board[r][c] == AI_PIECE: 
				pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
	pygame.display.update()


board = create_board()
print_board(board)
game_over = False


pygame.init()

SQUARESIZE = 100

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

turn = random.randint(PLAYER, AI)

while not game_over:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

		if event.type == pygame.MOUSEMOTION:
			pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
			posx = event.pos[0]
			if turn == PLAYER:
				pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)

		pygame.display.update()

		if event.type == pygame.MOUSEBUTTONDOWN:
			pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
			#print(event.pos)
			# Ask for Player 1 Input
			if turn == PLAYER:
				posx = event.pos[0]
				col = int(math.floor(posx/SQUARESIZE))

				if is_valid_location(board, col):
					row = get_next_open_row(board, col)
					drop_piece(board, row, col, PLAYER_PIECE)

					if winning_move(board, PLAYER_PIECE):
						label = myfont.render("Player 1 wins!!", 1, RED)
						screen.blit(label, (40,10))
						game_over = True

					turn += 1
					turn = turn % 2

					print_board(board)
					draw_board(board)



	# Ask for Player 2 Input
	if turn == AI and not game_over:	

		# col = random.randint(0, COLUMN_COUNT - 1)
		# col = pick_best_move(board, AI_PIECE)

        # First Call to minimax algo
		# Initializes alpha and beta as -inf and inf
		col, minimax_score = minimax(board, 5, -math.inf, math.inf , True)

		if is_valid_location(board, col):

			# Delay Before AI drops piece
			pygame.time.wait(500)

			row = get_next_open_row(board, col)
			drop_piece(board, row, col, AI_PIECE)

			if winning_move(board, AI_PIECE):
				label = myfont.render("Player 2 wins!!", 1, YELLOW)
				screen.blit(label, (40,10))
				game_over = True

			print_board(board)
			draw_board(board)

			turn += 1
			turn = turn % 2

	if game_over:
		pygame.time.wait(3000)


# CODE PROBLEMS
# 1. Next player piece doesnt show up until mouse moves
# 2. When user places piece in full column nothing happens but turn variable still incrememnts and player loses their turn
# ^ This one fixed cuz the turn is not changed if u use AI and misinput piece

# I think minimax is looking to get max points so it ends up trying to get extra points when has a clear opportunity to finish the game

# These can be fixed but I wont cuz I am interested only in the AI component of this project


# U CAN USE WIKIPEDIA OR MANY OTHER RESOURSES TO GET PSEUDO CODE FOR ANY DATA STRUCTURE

# ADD ALPHA BETA PRUNING