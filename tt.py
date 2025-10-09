EXACT, LOWER, UPPER = 0,1,2
TT = {}
DEPTH, FLAG, SCORE, MOVE = 0,1,2,3

def key(board_arr, side_to_move): #get hashable key
    return (board_arr.shape, board_arr.tobytes(order="C"), int(side_to_move)) 

def probe(key, depth, alpha, beta): 
    value = TT.get(key)#get value from the hash table
    if value and value[DEPTH] >= depth:#only trust if it is a deeper search
        score, flag = value[SCORE], value[FLAG]
        if flag == EXACT or (flag == LOWER and  score>= beta) or (flag == UPPER and score <= alpha):
            return score, value[MOVE]
    if value:
        return value[MOVE]
    else:
        return None

def store(key, depth, alpha0, beta0, score):
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
