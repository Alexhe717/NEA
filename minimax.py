import math
import os
from concurrent.futures import ProcessPoolExecutor
from typing import Optional
from dataclasses import dataclass
import numpy as np

import board
import tt
DIRECTIONS = ((1, 0), (0, 1), (1, 1), (1, -1))
WIN_SCORE = 1_000_000


def tt_memory(max_memory=4096):
    tt.assign_memory(max_memory=max_memory)


@dataclass
class Config:
    max_depth: Optional[int] = None
    candidate_radius: int = 2
    root_candidate_limit: int = 18
    child_candidate_limit: int = 10
    max_cores: Optional[int] = None
    max_memory: int = 4096
    parallel: bool = True


DEFAULT_CONFIG = Config()
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
	pruned = []
	for (x, y) in moves:
		has_neighbour = False
		for dx in (-1, 0, 1):
			for dy in (-1, 0, 1):
				if dx == 0 and dy == 0: 
					continue
				xx, yy = x + dx, y + dy
				if 0 <= xx < current_board.dimension and 0 <= yy < current_board.dimension and current_board.board_array[xx][yy] != 0:
					has_neighbour = True
					break
			if has_neighbour: 
				break
		if has_neighbour:
			pruned.append((x, y))
	return pruned if pruned else list(moves)

def adaptive_search_depth(current_board:board.Board):
	stones=np.count_nonzero(current_board.board_array)
	if stones <= 2:  return 4
	if stones <= 6:  return 6
	if stones <= 9:  return 7
	return 6

def best_move(current_board: board.Board,ai_piece):
	search_depth=adaptive_search_depth(current_board)
	best_score=-math.inf
	best_i,best_j=None,None
	for i,j in move_filter(current_board,2):
		current_board.change_state(i,j,ai_piece)
		score=minimax(current_board,0,False,-math.inf,math.inf,ai_piece,search_depth,last_move=(i,j,ai_piece))
		if score>best_score:
			best_score=score
			best_i=i
			best_j=j
		current_board.change_state(i,j,0)
	return best_i,best_j

def minimax(current_board: board.Board,depth,is_maximising,alpha:int,beta:int,ai_piece,max_depth,last_move):
	opponent_piece=opponent(ai_piece)
	if is_maximising:
		side_to_move= ai_piece
	else:
		side_to_move=opponent_piece
	if max_depth is None:
		depth_left=None
	else:
		depth_left=max_depth-depth
	key=tt.key(current_board.board_array,side_to_move)
	tt_value=tt.probe(key,depth_left,alpha,beta)
	if tt_value is not None:
		return tt_value
	if last_move is not None:
		lx,ly,lp=last_move
		if current_board.check_win_from(lx,ly,lp):
			if lp==ai_piece:
				return 100000-depth
			else:
				return -100000+depth
	if (max_depth is not None) and (depth>=max_depth):
		lx=None
		ly=None
		if last_move is not None:
			lx,ly,_=last_move
		return evaluation(current_board,ai_piece,lx,ly)
	alpha0,beta0=alpha,beta
	if is_maximising:
		best_score=-math.inf
		moves=order_evaluation(current_board, move_filter(current_board, 3), ai_piece)
		if not moves:
			return 0
		for i,j in moves:
			current_board.change_state(i,j,ai_piece)
			score=minimax(current_board,depth+1,False,alpha,beta,ai_piece,max_depth,last_move=(i,j,ai_piece))
			current_board.change_state(i,j,0)
			if score > best_score:
				best_score = score
			if best_score > alpha:
				alpha = best_score
			if beta <= alpha:
				tt.store(key, depth_left, alpha0, beta0, best_score)
				return best_score
		tt.store(key,depth_left,alpha0,beta0,best_score)
		return best_score
	else:
		best_score=math.inf
		moves=order_evaluation(current_board, move_filter(current_board, 3), opponent_piece)
		if not moves:
			return 0
		for i,j in moves:
			current_board.change_state(i,j,opponent_piece)
			score=minimax(current_board,depth+1,True,alpha,beta,ai_piece,max_depth,last_move=(i,j,opponent_piece))
			current_board.change_state(i,j,0)
			if score < best_score:
				best_score = score
			if best_score < beta:
				beta = best_score
			if beta <= alpha:
				tt.store(key,depth_left,alpha0,beta0,best_score)
				return best_score
		tt.store(key,depth_left,alpha0,beta0,best_score)
		return best_score
	
def opponent(piece):
	if piece==1:
		return 2
	if piece==2:
		return 1
	
def count_pieces_in_line(current_board: board.Board, x, y, piece, dx, dy):
	if x is None or y is None:
		return 0
	if current_board.board_array[x][y] != piece:
		return 0

	n = current_board.dimension
	cnt = 1

	i, j = x + dx, y + dy
	while 0 <= i < n and 0 <= j < n and current_board.board_array[i][j] == piece:
		cnt += 1
		i += dx
		j += dy

	i, j = x - dx, y - dy
	while 0 <= i < n and 0 <= j < n and current_board.board_array[i][j] == piece:
		cnt += 1
		i -= dx
		j -= dy

	return cnt

def evaluation(current_board: board.Board,ai_piece,x,y):
	if x is None or y is None:
		return 0

	target = current_board.condition - 1
	opp = opponent(ai_piece)
	directions = [(1,0),(0,1),(1,1),(1,-1)]

	for dx, dy in directions:
		if count_pieces_in_line(current_board, x, y, opp, dx, dy) >= target:
			return -5


	for dx, dy in directions:
		if count_pieces_in_line(current_board, x, y, ai_piece, dx, dy) >= target:
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



				
