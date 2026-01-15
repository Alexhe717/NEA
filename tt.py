EXACT, LOWER, UPPER = 0,1,2
TT = {}
DEPTH, FLAG, SCORE = 0,1,2
MAX_TT_SIZE = 1000000
def key(board_arr, side_to_move): #get hashable key
    return (board_arr.shape, board_arr.tobytes(order="C"), int(side_to_move)) 

def probe(key, depth, alpha, beta): 
    value = TT.get(key)#get value from the hash table
    if value and value[DEPTH] >= depth:#only trust if it is a deeper search
        score, flag = value[SCORE], value[FLAG]
        if flag == EXACT:
            return score
        if flag == LOWER and score >= beta:
            return score
        if flag == UPPER and score <= alpha:
            return score
    return None

def store(key, depth, alpha0, beta0, score):
    if len(TT) > MAX_TT_SIZE:
        TT.clear()
    if alpha0 < score < beta0:
        flag=EXACT
    elif score >=beta0:
        flag=LOWER
    else:
        flag=UPPER
    current = TT.get(key)
    if (current is None) or (depth >= current[DEPTH]):#if deeper or no current key then overwrite
        TT[key] = (depth, flag, score)
def clear():
    TT.clear()
