import numpy as np
class Board:
    def __init__(self,dimension):
        self.dimension=dimension
        self.condition=4
        self.board_array=np.zeros([dimension,dimension],dtype=np.int8)
    def display(self):
        print(self.board_array)
    def change_state(self,x,y,piece):
        self.board_array[x][y]=piece
    def check_draw(self):
        for i in range(self.dimension):
            for j in range(self.dimension):
                if self.board_array[i][j]==0:
                    return False
        return True
    def check_win_from(self, x, y, piece):
        if x is None or y is None: 
            return False
        n = self.dimension
        target = self.condition

        def count_direction(dx, dy):
            cnt = 1
            i, j = x + dx, y + dy
            while 0 <= i < n and 0 <= j < n and self.board_array[i][j] == piece:
                cnt += 1; 
                i += dx; 
                j += dy
            i, j = x - dx, y - dy
            while 0 <= i < n and 0 <= j < n and self.board_array[i][j] == piece:
                cnt += 1; 
                i -= dx; 
                j -= dy
            return cnt

        if count_direction(1, 0) >= target:
            return True
        if count_direction(0, 1) >= target:
            return True
        if count_direction(1, 1) >= target:
            return True
        if count_direction(1, -1) >= target:
            return True
        return False

# a=Board(3)

# a.change_state(0,0,1)
# a.change_state(1,1,1)
# a.change_state(1,2,1)
# a.change_state(0,1,2)
# a.change_state(1,0,2)
# a.change_state(2,2,2)
# print(a.board_array)
# print(a.check_win(2))
# # b=Board(5)

# b.change_state(0,4,3)
# b.change_state(1,3,3)
# b.change_state(2,2,3)
# b.change_state(3,1,3)
# b.change_state(4,0,3)
# print(b.board_array)
# print(b.check_win(3))

