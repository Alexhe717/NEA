import numpy as np
import tt
from typing import Optional

class Board:
	def __init__(self, dimension: int) -> None:
		self.dimension = dimension
		self.condition = 5
		self.board_array = np.zeros([dimension, dimension], dtype=np.int8)
		self.last_move = None
		self.empty_count = dimension * dimension
		tt.init_zobrist(dimension)
		self.current_hash = 0
		
	def display(self) -> None:
		print(self.board_array)
		
	def get_board_state(self) -> np.ndarray:
		return self.board_array.copy()
	
	def change_state(self, x: int, y: int, piece: int) -> None:
		if not (0 <= x < self.dimension and 0 <= y < self.dimension):
			raise IndexError(f"Move ({x}, {y}) is out of bounds for board size {self.dimension}")
		if piece not in [0, 1, 2]:
			raise ValueError(f"Invalid piece type: {piece}")
		old = self.board_array[x][y]
		if old != 0: #when piece is removed by minimax
			self.current_hash ^= tt.ZOBRIST_TABLE[(x, y, old)]
			self.empty_count += 1
		if piece != 0: #when new piece is played
					self.current_hash ^= tt.ZOBRIST_TABLE[(x, y, piece)]
					if old == 0:
						self.empty_count -= 1 
		self.board_array[x][y] = piece

	def check_draw(self) -> bool:
		return self.empty_count == 0 #no available space for a new move
	
	def check_win_from(self, x: Optional[int], y: Optional[int], piece: int) -> bool:
		if x is None or y is None: 
			return False
		n = self.dimension

		def count_direction(dx: int, dy: int) -> int: #counts consecutive pieces given a direction
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
		# count in four directions
		if count_direction(1, 0) >= self.condition:
			return True
		if count_direction(0, 1) >= self.condition:
			return True
		if count_direction(1, 1) >= self.condition:
			return True
		if count_direction(1, -1) >= self.condition:
			return True
		return False #if win condition is not met