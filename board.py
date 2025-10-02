import numpy as np
class Board:
    def __init__(self,dimension):
        self.dimension=dimension
        self.condition=3
        self.board_array=np.zeros([dimension,dimension],dtype=np.int8)
        self.last_move=None
    def display(self):
        print(self.board_array)
    def change_state(self,x,y,piece):
        self.board_array[x][y]=piece
        if piece != 0:
            self.last_move = (x, y, piece)

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

        if count_direction(1, 0) >= self.condition:
            return True
        if count_direction(0, 1) >= self.condition:
            return True
        if count_direction(1, 1) >= self.condition:
            return True
        if count_direction(1, -1) >= self.condition:
            return True
        return False

