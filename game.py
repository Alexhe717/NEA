import board
class Player:
    def __init__(self,name,piece):
        self.name=name
        self.piece=piece
    def move(self,x,y):
        board.Board.change_state(x,y,self.piece)
Player_a=Player("player_a","A")
Player_b=Player("Player_B","B")
class Game:
    def __init__(self,board_dimension):
        self.current_board=board.Board(board_dimension,board_dimension)
    def start(self):
        while True:
            if(self.current_board.check_win(Player_a)):
                return "player_A won"
            if(self.current_board.check_win(Player_b)):
                return "player_B won"

    
        