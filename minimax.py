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

def best_move(current_board: board.Board, ai_piece, config: Config = None):
    config = config or DEFAULT_CONFIG
    tt.assign_memory(max_memory=config.max_memory)

    search_depth = config.max_depth or adaptive_search_depth(current_board)
    root_moves = order_evaluation(
        current_board,
        move_filter(current_board, radius=config.candidate_radius),
        ai_piece,
        limit=config.root_candidate_limit,
    )
    if not root_moves:
        return None, None

    if len(root_moves) == 1:
        return int(root_moves[0][0]), int(root_moves[0][1])

    max_cores = config.max_cores or max(1, min((os.cpu_count() or 1) - 2, len(root_moves)))
    use_parallel = config.parallel and max_cores > 1 and len(root_moves) >= 2

    if use_parallel:
        per_core_memory = max(128, config.max_memory // max_cores)
        tasks = [
            (
                current_board.get_board_state(),
                current_board.dimension,
                ai_piece,
                move,
                search_depth,
                per_core_memory,
                config.child_candidate_limit,
                config.candidate_radius,
            )
            for move in root_moves
        ]
        with ProcessPoolExecutor(max_workers=max_cores) as pool:
            results = list(pool.map(parallel_evaluation, tasks, chunksize=1))
        best_score, best_row, best_col = max(results, key=lambda item: item[0])
        return int(best_row), int(best_col)

    best_score = -math.inf
    best_row, best_col = root_moves[0]
    for row, col in root_moves:
        current_board.change_state(row, col, ai_piece)
        score = minimax(
            current_board,
            0,
            False,
            -math.inf,
            math.inf,
            ai_piece,
            search_depth,
            (row, col, ai_piece),
            config,
        )
        current_board.change_state(row, col, 0)
        if score > best_score:
            best_score = score
            best_row, best_col = row, col
    return int(best_row), int(best_col)

def minimax(
    current_board: board.Board,
    depth,
    is_maximising,
    alpha,
    beta,
    ai_piece,
    max_depth,
    last_move,
    config: Config,
):
    side_to_move = ai_piece if is_maximising else opponent(ai_piece)
    depth_left = max_depth - depth
    hash_key = tt.key(current_board.board_array, side_to_move)
    tt_value = tt.probe(hash_key, depth_left, alpha, beta)
    if tt_value is not None:
        return tt_value

    if last_move is not None:
        last_row, last_col, last_piece = last_move
        if current_board.check_win_from(last_row, last_col, last_piece):
            if last_piece == ai_piece:
                return WIN_SCORE - depth
            return -WIN_SCORE + depth

    if depth >= max_depth or current_board.check_draw():
        last_row, last_col = (last_move[0], last_move[1]) if last_move is not None else (None, None)
        return evaluate_last_move(current_board, ai_piece, last_row, last_col)

    orig_alpha, orig_beta = alpha, beta
    moves = move_filter(current_board, config.candidate_radius)
    limit = config.child_candidate_limit
    
    if is_maximising:
        ordered = order_evaluation(current_board, moves, ai_piece, limit=limit)
        if not ordered:
            return 0
        best_score = -math.inf
        for row, col in ordered:
            current_board.change_state(row, col, ai_piece)
            score = minimax(current_board, depth + 1, False, alpha, beta, ai_piece, max_depth, (row, col, ai_piece), config)
            current_board.change_state(row, col, 0)
            if score > best_score:
                best_score = score
            if best_score > alpha:
                alpha = best_score
            if beta <= alpha:
                break
        tt.store(hash_key, depth_left, orig_alpha, orig_beta, int(best_score))
        return int(best_score)

    opp_piece = opponent(ai_piece)
    ordered = order_evaluation(current_board, moves, opp_piece, limit=limit)
    if not ordered:
        return 0
    best_score = math.inf
    for row, col in ordered:
        current_board.change_state(row, col, opp_piece)
        score = minimax(current_board, depth + 1, True, alpha, beta, ai_piece, max_depth, (row, col, opp_piece), config)
        current_board.change_state(row, col, 0)
        if score < best_score:
            best_score = score
        if best_score < beta:
            beta = best_score
        if beta <= alpha:
            break
    tt.store(hash_key, depth_left, orig_alpha, orig_beta, int(best_score))
    return int(best_score)

	
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

def parallel_evaluation(task):
    board_array, dimension, ai_piece, move, max_depth, max_memory, child_candidate_limit, radius = task
    tt.clear()
    tt.assign_memory(max_memory=max_memory)

    sim_board = board.Board(dimension)
    sim_board.board_array[:, :] = board_array
    sim_board.empty_count = int(np.count_nonzero(board_array == 0))

    row, col = move
    sim_board.change_state(row, col, ai_piece)

    local_config = Config(
        max_depth=max_depth,
        candidate_radius=radius,
        root_candidate_limit=0,
        child_candidate_limit=child_candidate_limit,
        parallel=False,
        max_memory=max_memory,
    )
    score = minimax(
        sim_board,
        depth=0,
        is_maximising=False,
        alpha=-math.inf,
        beta=math.inf,
        ai_piece=ai_piece,
        max_depth=max_depth,
        last_move=(row, col, ai_piece),
        config=local_config,
    )
    return score, row, col


				
