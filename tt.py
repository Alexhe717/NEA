from collections import OrderedDict
import random
from typing import Optional

EXACT, LOWER, UPPER = 0, 1, 2
DEPTH, FLAG, SCORE = 0, 1, 2
MAX_TT_SIZE = 100000
_APPROX_ENTRY_BYTES = 96
ZOBRIST_TABLE = {}
ZOBRIST_TURN = random.getrandbits(64)
TT = OrderedDict()

def assign_memory(max_memory: int = 512) -> None:
    global MAX_TT_SIZE
    max_memory_bytes = max(16, int(max_memory)) * 1024 * 1024
    MAX_TT_SIZE = max(50_000, max_memory_bytes // _APPROX_ENTRY_BYTES)
    if len(TT) > MAX_TT_SIZE:
        trim()

def trim() -> None:
    while len(TT) > MAX_TT_SIZE:
        TT.popitem(last=False)

def init_zobrist(dimension: int) -> None:
    if ZOBRIST_TABLE: return 
    
    random.seed(42)
    for r in range(dimension):
        for c in range(dimension):
            ZOBRIST_TABLE[(r, c, 1)] = random.getrandbits(64)
            ZOBRIST_TABLE[(r, c, 2)] = random.getrandbits(64)

def key(board_hash: int, side_to_move: int) -> int:
    if side_to_move == 1:
        return board_hash ^ ZOBRIST_TURN
    return board_hash

def probe(hash_key: int, depth: int, alpha: float, beta: float) -> Optional[int]:
    value = TT.get(hash_key)
    if value is None:
        return None
    TT.move_to_end(hash_key)

    if value[DEPTH] >= depth:
        score, flag = value[SCORE], value[FLAG]
        if flag == EXACT:
            return score
        if flag == LOWER and score >= beta:
            return score
        if flag == UPPER and score <= alpha:
            return score
    return None

def store(hash_key: int, depth: int, alpha0: float, beta0: float, score: int) -> None:
    if alpha0 < score < beta0:
        flag = EXACT
    elif score >= beta0:
        flag = LOWER
    else:
        flag = UPPER

    current = TT.get(hash_key)
    if (current is None) or (depth >= current[DEPTH]):
        TT[hash_key] = (depth, flag, score)
        TT.move_to_end(hash_key)
        if len(TT) > MAX_TT_SIZE:
            trim()

def clear() -> None:
    TT.clear()