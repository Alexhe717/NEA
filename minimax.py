import board
import game
import math
def best_move(current_board: board.Board,ai_piece):
    best_score=-9999
    best_i,best_j=None,None
    for i in range(current_board.dimension):
        for j in range(current_board.dimension):
            if current_board.board_array[i][j]==0:
                current_board.change_state(i,j,ai_piece)
                score=minimax(current_board,0,False,ai_piece)
                if score>best_score:
                    best_score=score
                    best_i=i
                    best_j=j
                current_board.change_state(i,j,0)
    return best_i,best_j

def minimax(current_board: board.Board,depth,is_maximising,ai_piece):
    opponent_piece=opponent(ai_piece)
    if current_board.check_win(ai_piece):
        return 10-depth
    if current_board.check_win(opponent_piece):
        return -10+depth
    if current_board.check_draw():
        return 0
    if is_maximising:
        best_score=-math.inf
        for i in range(current_board.dimension):
            for j in range(current_board.dimension):
                if current_board.board_array[i][j]==0:
                    current_board.change_state(i,j,ai_piece)
                    score=minimax(current_board,depth+1,False,ai_piece)
                    current_board.change_state(i,j,0)
                    best_score=max(best_score,score)
        return best_score
    else:
        best_score=math.inf
        for i in range(current_board.dimension):
            for j in range(current_board.dimension):
                if current_board.board_array[i][j]==0:
                    current_board.change_state(i,j,opponent_piece)
                    score=minimax(current_board,depth+1,True,ai_piece)
                    current_board.change_state(i,j,0)
                    best_score=min(best_score,score)
        return best_score
def opponent(piece):
    if piece==1:
        return 2
    if piece==2:
        return 1



