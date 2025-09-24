import board
import game
import math
def best_move(current_board: board.Board,ai_piece):
    best_score=-math.inf
    best_i,best_j=None,None
    for i in range(current_board.dimension):
        for j in range(current_board.dimension):
            if current_board.board_array[i][j]==0:
                current_board.change_state(i,j,ai_piece)
                score=minimax(current_board,0,False,-math.inf,math.inf,ai_piece,max_depth=2)
                if score>best_score:
                    best_score=score
                    best_i=i
                    best_j=j
                current_board.change_state(i,j,0)
    return best_i,best_j

def minimax(current_board: board.Board,depth,is_maximising,alpha:int,beta:int,ai_piece,max_depth):
    opponent_piece=opponent(ai_piece)
    if current_board.check_win(ai_piece):
        return 10-depth
    if current_board.check_win(opponent_piece):
        return -10+depth
    if current_board.check_draw():
        return 0
    if (max_depth is not None) and (depth>=max_depth):
        return evaluation(current_board,ai_piece)
    if is_maximising:
        best_score=-math.inf
        for i in range(current_board.dimension):
            for j in range(current_board.dimension):
                if current_board.board_array[i][j]==0:
                    current_board.change_state(i,j,ai_piece)
                    score=minimax(current_board,depth+1,False,alpha,beta,ai_piece,max_depth)
                    current_board.change_state(i,j,0)
                    best_score=max(best_score,score)
                    alpha=max(alpha,best_score)
                    if beta<=alpha:
                        return best_score
        return best_score
    else:
        best_score=math.inf
        for i in range(current_board.dimension):
            for j in range(current_board.dimension):
                if current_board.board_array[i][j]==0:
                    current_board.change_state(i,j,opponent_piece)
                    score=minimax(current_board,depth+1,True,alpha,beta,ai_piece,max_depth)
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

def evaluation(current_board: board.Board,ai_piece):
    for i in range(current_board.dimension):
        num_of_consecutives=0
        for j in range(current_board.dimension):
            if current_board.board_array[i][j]==ai_piece:
                num_of_consecutives+=1
            else:
                num_of_consecutives=0
        if num_of_consecutives==current_board.condition-1: #checking for 4 in a row
            return 5
    for i in range(current_board.dimension):
        num_of_consecutives=0
        for j in range(current_board.dimension):
            if current_board.board_array[j][i]==ai_piece:
                num_of_consecutives+=1
            else:
                num_of_consecutives=0
        if num_of_consecutives==current_board.condition-1: #checking for 4 in a row
            return 5
    for i in range(current_board.dimension):
            for j in range(current_board.dimension):
                num_of_consecutives=0
                row,collum=i,j
                while row+1<current_board.dimension and collum+1<current_board.dimension:
                    if current_board.board_array[row][collum]==ai_piece and current_board.board_array[row+1][collum+1]==ai_piece:
                        num_of_consecutives+=1
                    else:
                        num_of_consecutives=0
                    row+=1
                    collum+=1
                if num_of_consecutives==current_board.condition-2:
                    return 5
    for i in range(current_board.dimension):
        for j in range(current_board.dimension):
            num_of_consecutives=0
            row,collum=i,j
            while row+1<current_board.dimension and collum-1<current_board.dimension and collum-1>=0:
                if current_board.board_array[row][collum]==ai_piece and current_board.board_array[row+1][collum-1]==ai_piece:
                    num_of_consecutives+=1
                else:
                    num_of_consecutives=0
                row+=1
                collum-=1
            if num_of_consecutives==current_board.condition-2:
                return 5
    opp_piece=opponent(ai_piece)
    for i in range(current_board.dimension):
        num_of_consecutives=0
        for j in range(current_board.dimension):
            if current_board.board_array[i][j]==opp_piece:
                num_of_consecutives+=1
            else:
                num_of_consecutives=0
        if num_of_consecutives==current_board.condition-1: #checking for 4 in a row
            return -5
    for i in range(current_board.dimension):
        num_of_consecutives=0
        for j in range(current_board.dimension):
            if current_board.board_array[j][i]==opp_piece:
                num_of_consecutives+=1
            else:
                num_of_consecutives=0
        if num_of_consecutives==current_board.condition-1: #checking for 4 in a row
            return -5
    for i in range(current_board.dimension):
        for j in range(current_board.dimension):
            num_of_consecutives=0
            row,collum=i,j
            while row+1<current_board.dimension and collum+1<current_board.dimension:
                if current_board.board_array[row][collum]==opp_piece and current_board.board_array[row+1][collum+1]==opp_piece:
                    num_of_consecutives+=1
                else:
                    num_of_consecutives=0
                row+=1
                collum+=1
            if num_of_consecutives==current_board.condition-2:
                return -5
    for i in range(current_board.dimension):
        for j in range(current_board.dimension):
            num_of_consecutives=0
            row,collum=i,j
            while row+1<current_board.dimension and collum-1<current_board.dimension and collum-1>=0:
                if current_board.board_array[row][collum]==opp_piece and current_board.board_array[row+1][collum-1]==opp_piece:
                    num_of_consecutives+=1
                else:
                    num_of_consecutives=0
                row+=1
                collum-=1
            if num_of_consecutives==current_board.condition-2:
                return -5