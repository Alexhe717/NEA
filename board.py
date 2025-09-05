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
        for i in range(self.row):
            num_of_consecutives=0
            for j in range(self.collum):
                if self.board_array[i][j]==piece:
                    num_of_consecutives+=1
                else:
                    num_of_consecutives=0
            if num_of_consecutives==5:
                return True
        for i in range(self.collum):
            num_of_consecutives=0
            for j in range(self.row):
                if self.board_array[i][j]==piece:
                    num_of_consecutives+=1
                else:
                    num_of_consecutives=0
            if num_of_consecutives==5:
                return True
        
        for i in range(self.row):
            for j in range(self.collum):
                num_of_consecutives=0
                row,collum=i,j
                while row+1<self.row and collum+1<self.collum:
                    if self.board_array[row][collum]==piece and self.board_array[row+1][collum+1]==piece:
                        num_of_consecutives+=1
                    else:
                        num_of_consecutives=0
                    row+=1
                    collum+=1
                if num_of_consecutives==4:
                    return True
        for i in range(self.row):
            for j in range(self.collum):
                num_of_consecutives=0
                row,collum=i,j
                while row+1<self.row and collum-11<self.collum:
                    if self.board_array[row][collum]==piece and self.board_array[row+1][collum-1]==piece:
                        num_of_consecutives+=1
                    else:
                        num_of_consecutives=0
                    row+=1
                    collum-=1
                if num_of_consecutives==4:
                    return True
        return False

a=Board(5,5)

a.change_state(0,0,3)
a.change_state(1,1,3)
a.change_state(2,2,3)
a.change_state(3,3,3)
a.change_state(4,4,3)
print(a.board_array)
print(a.check_win(3))
b=Board(5,5)

b.change_state(0,4,3)
b.change_state(1,3,3)
b.change_state(2,2,3)
b.change_state(3,1,3)
b.change_state(4,0,3)
print(b.board_array)
print(b.check_win(3))

