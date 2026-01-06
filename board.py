import numpy as np
class Board:
	def __init__(self,dimension):
		self.dimension=dimension
		self.condition=3
		self.board_array=np.zeros([dimension,dimension],dtype=np.int8)
		self.last_move=None
		self.empty_count = dimension * dimension
	def display(self):
		print(self.board_array)
	def change_state(self,x,y,piece):
		old = self.board_array[x][y]
		if old == 0 and piece != 0: self.empty_count -= 1
		if old != 0 and piece == 0: self.empty_count += 1
		self.board_array[x][y] = piece

	def check_draw(self):
		return self.empty_count == 0
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

