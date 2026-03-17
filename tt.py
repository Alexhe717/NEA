from collections import OrderedDict
import hashlib
EXACT, LOWER, UPPER = 0,1,2
DEPTH, FLAG, SCORE = 0,1,2
MAX_TT_SIZE = 100000
_APPROX_ENTRY_BYTES = 96
TT = OrderedDict()
def assign_memory(max_memory: int = 512):
    global MAX_TT_SIZE
    max_memory_bytes = max(16, int(max_memory)) * 1024 * 1024
    MAX_TT_SIZE = max(50_000, max_memory_bytes // _APPROX_ENTRY_BYTES)
    if len(TT) > MAX_TT_SIZE:
        trim()


def trim():
    while len(TT) > MAX_TT_SIZE:
        TT.popitem(last=False)

def key(board_arr, side_to_move: int):
    h = hashlib.blake2b(digest_size=8)
    h.update(board_arr.tobytes(order='C'))
    h.update(bytes((int(side_to_move), board_arr.shape[0] & 0xFF, board_arr.shape[1] & 0xFF)))
    return int.from_bytes(h.digest(), 'little', signed=False)

def probe(hash_key: int, depth: int, alpha: int, beta: int):
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

def store(hash_key: int, depth: int, alpha0: int, beta0: int, score: int):
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

def clear():
    TT.clear()
