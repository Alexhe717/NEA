import board
import game
import math
# test_board=board.Board(5)
def best_move(current_board: board.Board,ai_piece):
    best_score=-9999
    best_i,best_j=None,None
    for i in range(current_board.dimension):
        for j in range(current_board.dimension):
            if current_board.board_array[i][j]==0:
                current_board.board_array[i][j]=ai_piece
                score=minimax(current_board,0,True,ai_piece)
                if score>best_score:
                    best_score=score
                    best_i=i
                    best_j=j
                current_board.board_array[i][j]=0
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
        best_score=-9999
        for i in range(current_board.dimension):
            for j in range(current_board.dimension):
                if current_board.board_array[i][j]==0:
                    current_board.board_array[i][j]=ai_piece
                    score=minimax(current_board,depth+1,False,ai_piece)
                    current_board.board_array[i][j]=0
                    best_score=max(best_score,score)
        return best_score
    else:
        best_score=9999
        for i in range(current_board.dimension):
            for j in range(current_board.dimension):
                if current_board.board_array[i][j]==0:
                    current_board.board_array[i][j]=opponent_piece
                    score=minimax(current_board,depth+1,True,ai_piece)
                    current_board.board_array[i][j]=0
                    best_score=min(best_score,score)
        return best_score
def opponent(piece):
    if piece==1:
        return 2
    if piece==2:
        return 1
a=board.Board(3)
a.change_state(0,0,1)
a.change_state(0,1,2)
a.change_state(0,2,1)
a.change_state(1,0,2)
a.change_state(1,1,1)
a.change_state(2,0,2)
a.display()
print(best_move(a,1))

b = board.Board(3)
b.change_state(0,0,2)
b.change_state(1,0,2)
b.change_state(1,1,1)
b.display()
print(best_move(b, 1)) 

c = board.Board(3)
c.display()
print(best_move(c, 1))

import board, minimax
e = board.Board(3)
e.change_state(0,0,1); e.change_state(0,1,2); e.change_state(0,2,1)
e.change_state(1,0,2); e.change_state(1,1,1); e.change_state(1,2,2)
e.change_state(2,0,2); e.change_state(2,1,1)
e.display()
print(best_move(e, 1))  # expect (2,2)

import board, minimax
f = board.Board(3)
f.change_state(1,1,1)
f.change_state(2,0,2); f.change_state(2,1,2)
f.display()
print(best_move(f, 2))  # expect (2,2)


import board, minimax
g = board.Board(3)
g.change_state(0,0,1); g.change_state(1,1,1)
g.display()
print(best_move(g, 2))  # expect (2,2)


