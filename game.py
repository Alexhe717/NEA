import board
import random
import numpy as np
class Player:
	def __init__(self,name,piece):
		self.name=name
		self.piece=piece
	def policy(self,board):
		board_dimension=np.size(board.board_array,0)
		return random.randint(0,board_dimension-1),random.randint(0,board_dimension-1)
class Game:
	def __init__(self,board_dimension):
		self.board_dimension=board_dimension
		self.current_board=board.Board(board_dimension)
		self.player_1=Player('1',1)
		self.player_2=Player('2',2)
	def check_if_cell_occupied(self,x,y):
		if self.current_board.board_array[x][y]==0:
			return True
		else:
			return False
	def get_policy_from_player(self,player):
		return player.policy(self.current_board)

	def make_move(self,player,board):
		x=None
		y=None
		while (x,y)==(None,None) or board.board_array[x][y]!=0:
			x,y=self.get_policy_from_player(player)
			self.last_x=x
			self.last_y=y
		board.change_state(x,y,player.piece)
	def game_start(self):
		players=[self.player_1,self.player_2]
		self.turn_number=0
		self.max_turn=self.board_dimension*self.board_dimension
		while True:
			self.make_move(players[self.turn_number%2],self.current_board)
			if self.current_board.check_win_from(self.last_x,self.last_y,players[self.turn_number%2]):
				print(f'{self.last_y,players[self.turn_number%2]} won')
			elif self.current_board.check_draw():
				print('draw')
			self.turn_number+=1
			self.current_board.display()
# a=Game(3)
# print(a.game_start())
		