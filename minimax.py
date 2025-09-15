import board
import game
import math
# test_board=board.Board(5)
def best_move(current_board: board.Board,curren_player:game.Player):
    best_score=-9999
    for i in range(current_board.dimension,curren_player.piece):
        for j in range(current_board.dimension):
            if current_board.board_array[i][j]==0:
                current_board.board_array[i][j]=curren_player.piece
                score=minimax()
                if score>best_score:
                    best_score=score
                    best_i=i
                    best_j=j
    return best_i,best_j


def minimax(current_board: board.Board,depth,is_maximising):
    if current_board.check_win(1):
        return 10
    if current_board.check_win(2):
        return -10
    if current_board.check_draw():
        return 0
    if is_maximising:
        best_score=-9999
        for i in range(current_board.dimension):
            for j in range(current_board.dimension):
                if current_board.board_array[i][j]==0:
                    current_board.board_array[i][j]=1
                    score=minimax(current_board,depth+1,False)
                    current_board.board_array[i][j]=0
                    best_score=max(best_score,score)
        return best_score
    else:
        best_score=9999
        for i in range(current_board.dimension):
            for j in range(current_board.dimension):
                if current_board.board_array[i][j]==0:
                    current_board.board_array[i][j]=2
                    score=minimax(current_board,depth+1,True)
                    current_board.board_array[i][j]=0
                    best_score=max(best_score,score)
        return best_score
                    


