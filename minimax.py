import board
import game
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



def minimax()
