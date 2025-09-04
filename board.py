import numpy as np
class Board:
    def __init__(self,row,collum):
        self.row=row
        self.collum=collum
        self.board_array=np.zeros([row,collum])
    def display(self):
        print(self.board_array)
    def change_state(self,x,y,piece):
        self.board_array[x][y]=piece
    def check_win(self,piece):
        for i in self.row:
            num_of_consecutives=0
            for j in self.collum:
                if self.board_array[i][j]==piece:
                    num_of_consecutives+1
            if num_of_consecutives==5:
                return True
        for i in self.collum:
            num_of_consecutives=0
            for j in self.row:
                if self.board_array[i][j]==piece:
                    num_of_consecutives+1
            if num_of_consecutives==5:
                return True
        
        
                

a=Board(5,5)
a.change_state(0,0,3)
a.change_state(0,1,3)
a.change_state(0,2,3)
a.change_state(0,3,3)
a.change_state(0,4,3)
print(a.board_array)
print(a.check_win(3))

