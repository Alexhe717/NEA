import board
import tt
import minimax
class Player:
	def __init__(self,name,piece):
		self.name=name
		self.piece=piece
	def policy(self,current_board:board.Board):
		if self.name=='human':
			raise ValueError(f'The human input is handled by the ui')
		if self.name=='ai':
			return minimax.best_move(current_board, self.piece)
		raise ValueError(f'Unknown player type: {self.name}')
class Game:
	def __init__(self,board_dimension,win_condition=5):
		self.board_dimension = board_dimension
		self.current_board = board.Board(board_dimension)
		self.current_board.condition = win_condition
		self.player_1 = Player('human', 1)
		self.player_2 = Player('ai', 2)
		self.players = [self.player_1, self.player_2]

		self.turn_number = 0
		self.last_move = None
		tt.clear()
	@property
	def current_player(self):
		return self.players[self.turn_number % 2]

	def make_move(self, x, y):
		player = self.current_player
		self.current_board.change_state(x, y, player.piece)
		self.last_move = (x, y)
		self.turn_number += 1
		return 'win' if self.current_board.check_win_from(x, y, player.piece) else 'draw' if self.current_board.check_draw() else 'continue'

