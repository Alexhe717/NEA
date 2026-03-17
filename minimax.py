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

def move_filter(current_board: board.Board, radius=2):
    occupied = np.argwhere(current_board.board_array != 0)
    if occupied.size == 0:
        centre = current_board.dimension // 2
        return [(centre, centre)]

    moves = set()
    board_size = current_board.dimension
    for row, col in occupied:
        for d_row in range(-radius, radius + 1):
            for d_col in range(-radius, radius + 1):
                r, c = row + d_row, col + d_col
                if 0 <= r < board_size and 0 <= c < board_size and current_board.board_array[r][c] == 0:
                    moves.add((int(r), int(c)))

    pruned = []
    for row, col in moves:
        has_neighbour = False
        for d_row in (-1, 0, 1):
            for d_col in (-1, 0, 1):
                if d_row == 0 and d_col == 0:
                    continue
                adj_row, adj_col = row + d_row, col + d_col
                if 0 <= adj_row < board_size and 0 <= adj_col < board_size and current_board.board_array[adj_row][adj_col] != 0:
                    has_neighbour = True
                    break
            if has_neighbour:
                break
        if has_neighbour:
            pruned.append((row, col))
    return pruned if pruned else list(moves)

def adaptive_search_depth(current_board: board.Board):
    stones = np.count_nonzero(current_board.board_array)
    board_size = current_board.dimension
    if board_size <= 5:
        return 7
    if stones <= 2:
        return 4
    if stones <= 10:
        return 5
    if stones <= 24:
        return 6
    return 5

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
	
def line_info(grid, row, col, piece, d_row, d_col):
    board_size = grid.shape[0]
    streak = 1
    open_ends = 0

    check_row, check_col = row + d_row, col + d_col
    while 0 <= check_row < board_size and 0 <= check_col < board_size and grid[check_row, check_col] == piece:
        streak += 1
        check_row += d_row
        check_col += d_col
    if 0 <= check_row < board_size and 0 <= check_col < board_size and grid[check_row, check_col] == 0:
        open_ends += 1

    check_row, check_col = row - d_row, col - d_col
    while 0 <= check_row < board_size and 0 <= check_col < board_size and grid[check_row, check_col] == piece:
        streak += 1
        check_row -= d_row
        check_col -= d_col
    if 0 <= check_row < board_size and 0 <= check_col < board_size and grid[check_row, check_col] == 0:
        open_ends += 1

    return streak, open_ends

def pattern_score(streak, open_ends, win_condition):
    if streak >= win_condition:
        return WIN_SCORE
    if streak == win_condition - 1:
        if open_ends == 2:
            return 100_000
        if open_ends == 1:
            return 10_000
    if streak == win_condition - 2:
        if open_ends == 2:
            return 2_500
        if open_ends == 1:
            return 300
    if streak == win_condition - 3:
        if open_ends == 2:
            return 120
        if open_ends == 1:
            return 20
    if streak == 2 and open_ends == 2:
        return 8
    return 0

def total_move_score(current_board: board.Board, row, col, piece):
    grid = current_board.board_array
    win_condition = current_board.condition
    total = 0
    centre = current_board.dimension // 2
    total -= abs(row - centre) + abs(col - centre)

    for d_row, d_col in DIRECTIONS:
        streak, open_ends = line_info(grid, row, col, piece, d_row, d_col)
        total += pattern_score(streak, open_ends, win_condition)
    return total

def evaluate_last_move(current_board: board.Board, ai_piece, row, col):
    if row is None or col is None:
        return 0

    grid = current_board.board_array
    piece = grid[row, col]
    if piece == 0:
        return 0

    score = 0
    opp_piece = opponent(ai_piece)

    for d_row, d_col in DIRECTIONS:
        ai_streak, ai_open = line_info(grid, row, col, ai_piece, d_row, d_col) if piece == ai_piece else (0, 0)
        opp_streak, opp_open = line_info(grid, row, col, opp_piece, d_row, d_col) if piece == opp_piece else (0, 0)
        score += pattern_score(ai_streak, ai_open, current_board.condition)
        score -= pattern_score(opp_streak, opp_open, current_board.condition)

    return score

def order_evaluation(current_board: board.Board, moves, piece, limit=None):
    opp_piece = opponent(piece)
    wins, blocks, scored = [], [], []

    for row, col in moves:
        if current_board.board_array[row, col] != 0:
            continue

        current_board.change_state(row, col, piece)
        if current_board.check_win_from(row, col, piece):
            current_board.change_state(row, col, 0)
            wins.append((row, col))
            continue
        own_score = total_move_score(current_board, row, col, piece)
        current_board.change_state(row, col, 0)

        current_board.change_state(row, col, opp_piece)
        block_score = total_move_score(current_board, row, col, opp_piece)
        if current_board.check_win_from(row, col, opp_piece):
            current_board.change_state(row, col, 0)
            blocks.append((row, col))
            continue
        current_board.change_state(row, col, 0)

        scored.append(((own_score + block_score), (row, col)))

    scored.sort(key=lambda item: item[0], reverse=True)
    ordered = wins + blocks + [move for _, move in scored]
    if limit is not None:
        ordered = ordered[:limit]
    return ordered

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


				
