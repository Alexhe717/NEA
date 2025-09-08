import board
import random
import numpy as np
class Player:
	def __init__(self,name,piece):
		self.name=name
		self.piece=piece
	def policy(self,board_dimension):
		return random.randint(0,board_dimension-1),random.randint(0,board_dimension-1)
class Game:
	def __init__(self,board_dimension):
		self.player_1=Player('1',1)
		self.player_2=Player('2',2)
		self.board_dimension=board_dimension
		self.current_board=board.Board(board_dimension)
	def make_move(self,turn_number):
		if turn_number%2==0:#player 1
			self.current_board.change_state(*self.player_1.policy(self.board_dimension),self.player_1.piece)
		else:
			self.current_board.change_state(*self.player_2.policy(self.board_dimension),self.player_2.piece)
	def game_start(self):
		self.turn_number=0
		while True:
			if(self.current_board.check_win(self.player_1.piece)):
				return "player_A won"
			if(self.current_board.check_win(self.player_2.piece)):
				return "player_B won"
			self.make_move(self.turn_number)
			self.turn_number+=1
			self.current_board.display()

a=Game(10)
print(a.game_start())
		