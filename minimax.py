import board
import game
import math
import numpy as np
def move_filter(current_board: board.Board,radius):
	occupied=np.argwhere(current_board.board_array!=0)
	if occupied.size==0:
		return [(current_board.dimension//2,current_board.dimension//2)]
	moves=set()
	for i,j in occupied:
		for di in range(-radius,radius+1):
			for dj in range(-radius,radius+1):
				x,y=i+di,j+dj
				if 0<=x<current_board.dimension and 0<=y<current_board.dimension and current_board.board_array[x][y]==0:
					moves.add((x,y))
	return list(moves)


def best_move(current_board: board.Board,ai_piece):
	best_score=-math.inf
	best_i,best_j=None,None
	for i,j in move_filter(current_board,3):
		current_board.change_state(i,j,ai_piece)
		score=minimax(current_board,0,False,-math.inf,math.inf,ai_piece,10,last_move=(i,j,ai_piece))
		if score>best_score:
			best_score=score
			best_i=i
			best_j=j
		current_board.change_state(i,j,0)
	return best_i,best_j

def minimax(current_board: board.Board,depth,is_maximising,alpha:int,beta:int,ai_piece,max_depth,last_move):
	if last_move is not None:
		lx,ly,lp=last_move
		if current_board.check_win_from(lx,ly,lp):
			if lp==ai_piece:
				return 10-depth
			else:
				return -10+depth
	opponent_piece=opponent(ai_piece)
	if (max_depth is not None) and (depth>=max_depth):
		lx=None
		ly=None
		if last_move is not None:
			lx,ly,_=last_move
		return evaluation(current_board,ai_piece,lx,ly)
	if is_maximising:
		best_score=-math.inf
		moves=order_evaluation(current_board, move_filter(current_board, 2), ai_piece)
		if not moves:
			return 0
		for i,j in moves:
			current_board.change_state(i,j,ai_piece)
			score=minimax(current_board,depth+1,False,alpha,beta,ai_piece,max_depth,last_move=(i,j,ai_piece))
			current_board.change_state(i,j,0)
			best_score=max(best_score,score)
			alpha=max(alpha,best_score)
			if beta<=alpha:
				return best_score
		return best_score
	else:
		best_score=math.inf
		moves=order_evaluation(current_board, move_filter(current_board, 2), opponent_piece)
		if not moves:
			return 0
		for i,j in moves:
			current_board.change_state(i,j,opponent_piece)
			score=minimax(current_board,depth+1,True,alpha,beta,ai_piece,max_depth,last_move=(i,j,opponent_piece))
			current_board.change_state(i,j,0)
			best_score=min(best_score,score)
			beta=min(beta,best_score)
			if beta<=alpha:
				return best_score

		return best_score
def opponent(piece):
	if piece==1:
		return 2
	if piece==2:
		return 1

def evaluation(current_board: board.Board,ai_piece,x,y):
	if x is None or y is None: 
		return 0
	n = current_board.dimension
	target = current_board.condition-1
	def count_direction_ai_piece(dx, dy):
		cnt = 1 if current_board.board_array[x][y]==ai_piece else 0
		i, j = x + dx, y + dy
		while 0 <= i < n and 0 <= j < n and current_board.board_array[i][j] == ai_piece:
			cnt += 1; 
			i += dx; 
			j += dy
		i, j = x - dx, y - dy
		while 0 <= i < n and 0 <= j < n and current_board.board_array[i][j] == ai_piece:
			cnt += 1; 
			i -= dx; 
			j -= dy
		return cnt
	def count_direction_opp_piece(dx, dy):
		opponent_piece=opponent(ai_piece)
		cnt = 1 if current_board.board_array[x][y]==opponent else 0
		i, j = x + dx, y + dy
		while 0 <= i < n and 0 <= j < n and current_board.board_array[i][j] == opponent_piece:
			cnt += 1; 
			i += dx; 
			j += dy
		i, j = x - dx, y - dy
		while 0 <= i < n and 0 <= j < n and current_board.board_array[i][j] == opponent_piece:
			cnt += 1; 
			i -= dx; 
			j -= dy
		return cnt
	if count_direction_opp_piece(1, 0) >= target:
		return -5
	if count_direction_opp_piece(0, 1) >= target:
		return -5
	if count_direction_opp_piece(1, 1) >= target:
		return -5
	if count_direction_opp_piece(1, -1) >= target:
		return -5
	if count_direction_ai_piece(1, 0) >= target:
		return 5
	if count_direction_ai_piece(0, 1) >= target:
		return 5
	if count_direction_ai_piece(1, 1) >= target:
		return 5
	if count_direction_ai_piece(1, -1) >= target:
		return 5
	
	return 0

def order_evaluation(current_board: board.Board,moves,ai_piece):
	opponent_piece=opponent(ai_piece)
	wins,blocks,rests=[],[],[]
	def neighbour_count(i,j):
		count=0
		for di in (-1,0,1):
			for dj in (-1,0,1):
				if di==0 and dj==0:
					continue
				ii,jj=i+di,j+dj
				if 0<=ii<current_board.dimension and 0<=jj<current_board.dimension and current_board.board_array[ii][jj]!=0:
					count+=1
		centre=current_board.dimension//2
		mahhattan_distance=-(abs(i-centre)+abs(j-centre))
		return count,mahhattan_distance
	for (i,j) in moves:
		if current_board.board_array[i][j]!=0:
			continue
		current_board.board_array[i][j]=ai_piece
		if current_board.check_win_from(i,j,ai_piece):
			current_board.board_array[i][j]=0
			wins.append((i,j))
			continue
		current_board.board_array[i][j]=0
		current_board.board_array[i][j]=opponent_piece
		if current_board.check_win_from(i,j,opponent_piece):
			current_board.board_array[i][j]=0
			blocks.append((i,j))
			continue
		current_board.board_array[i][j]=0
		rests.append((i,j))
	rests.sort(key=lambda m: neighbour_count(*m), reverse=True)
	return wins+blocks+rests



				
