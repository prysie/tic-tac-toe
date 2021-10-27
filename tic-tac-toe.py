# -----------------------------------------------------------
# A fun little game of tic-tac-toe
# -----------------------------------------------------------

import re
import sys
from operator import attrgetter
from enum import Enum

class Win(str, Enum):
    ''' An Emunerated class that captures a Win and a user description
    '''
    NONE = 'None'
    ROW = 'Row Win'
    COL = 'Column Win'
    DIAG = 'Diagonal Win'
    DRAW = 'Drawn'

class Sym():    
    ''' A class to define a game symbol
        Note: The Equals method is overloaded to allow the default symbol to
        behave like a null equalivlent
    '''
    _symbol=None
    def __init__(self, symbol):
        self._symbol = symbol
        
    def __eq__(self, other):
        if self._symbol == '*': 
            return False 
        else:
            return self._symbol==other._symbol

    def __repr__(self):
        return self._symbol
    
    def __str__(self):
        return self._symbol
    
class UserMenuHelper:
    ''' A Menu helper class to display user menus
    '''    
    def display_main_menu(self):
        print('**********************************************')
        print('**       Welcome to Tic-Tac-Toe             **')
        print('**********************************************')
        print('**       Please make a menu selection:      **')            
        print('**                                          **')
        print('**     1. Begin the game                    **')
        print('**     2. Quit the game                     **')
        print('**                                          **')
        print('**********************************************')

    def display_lobby_menu(self):
        print('**********************************************')
        print('**         The game has begun               **')
        print('**********************************************')
        print('**  Please enter grid size (e.g. 3 for 3x3) **')
        print('**                                          **')
        print('**********************************************')
    
class InvalidInputError(Exception):
    ''' A custom Exception class for invalid input
    '''    
    pass

class Board:
    ''' The game board class, contains customised grid for playing
    '''    
    _empty_symbol = None 
    _dims = (0,0)
    _grid = None
    grid = property(attrgetter("_grid"))
    dims = property(attrgetter("_dims"))
    empty_symbol = property(attrgetter("_empty_symbol"))
    
    def __init__(self, dims):
        print('Creating Grid with dimensions: ' + str(dims[0]) + 'x' + str(dims[1]))
        self._dims = dims        
        self._empty_symbol = Sym('*')
        self._grid = [ [self._empty_symbol] * self._dims[0] for i in range(self._dims[1]) ]
        
    def get_grid_coordinates(self, position):
        ''' Given an absolute position returns a grid coordinate for the board
        '''
        if (position > (self.dims[0]*self.dims[1])):
            raise InvalidInputError
        co_x = int(position/self.dims[0])+1
        co_y = position%self.dims[0]
        if (position%self.dims[0] == 0):
            co_x = co_x -1 
        return (co_x,co_y)
    
    def display_board(board):
        for i in range(len(board)):   
            row=''
            for j in range(len(board[i])):
                row = row + str(board[i][j])
            print(row)

    def check_board(board, gameover):
        if gameover:
            return Win.DRAW
        
        for i in range(len(board.grid)):
            won_row = True        
            for j in range(len(board.grid[i])):
                won_row = all(x == board.grid[i][j] for x in board.grid[i]) and won_row
                if won_row:
                    return Win.ROW
                
        piv = [list(i) for i in zip(*board.grid)]
        for i in range(len(piv)):    
            won_col = True
            for j in range(len(piv[i])):                
                won_col = all(x == piv[i][j] for x in piv[i]) and won_col
            if won_col:
                return Win.COL        

        piv = [board.grid[x][x] for x in range(len(board.grid))]
        for i in range(len(piv)):
            won_diag = True
            won_diag = all(x == piv[i] for x in piv) and won_diag
            if won_diag:
                return Win.DIAG  
            
        rgrid = board.grid[::-1]
        piv = [rgrid[x][x] for x in range(len(rgrid))]
        for i in range(len(piv)):
            won_diag2 = True            
            won_diag2 = all(x == piv[i] for x in piv) and won_diag2
            if won_diag2:
                return Win.DIAG        
        return Win.NONE
    
class Player:
    ''' The game player
    '''    
    _symbol = None
    symbol = property(attrgetter("_symbol"))
    
    def __init__(self, symbol):
        self._symbol = symbol
        
    def _interaction(self):
        user_selection = input ("Enter position for player " + str(self._symbol) + ':')
        if re.match('^[1-9][0-9]?$|^100$', user_selection):              
            return int(user_selection)
        else:
            raise InvalidInputError            

    def update_board(self, board):
        player_postion=self._interaction() 
        gc = board.get_grid_coordinates(player_postion)                
        if board.grid[gc[0]-1][gc[1]-1] is board.empty_symbol :
            board.grid[gc[0]-1][gc[1]-1]=self.symbol
            turn=False
        else: 
            print (str(player_postion) + " " + "position has been taken by Player " + str(board.grid[gc[0]-1][gc[1]-1]))
            turn=True
        return turn
    
    def __str__(self):
        return str(self.symbol)
            
class GameState:
    ''' Game state controls game play and maintains state for player and board
    '''    
    __running=True
    __play=True
    __turn_count=0
    __p1 = None
    __p2 = None
    __active_player=None
    __active_board=None    
    __ui = None

    def __init__(self, p1, p2):        
        self.__ui = UserMenuHelper()
        self.__p1 = p1
        self.__p2 = p2
        self.__active_player = p2
        self.__turn_count=1
        self.game_lobby_loop()
    
    def turn(self, board):
        turn = True
        while turn:
            try:
                turn = self.__active_player.update_board(board)
                place = self.place(self.__active_player, board)
                if (place != Win.NONE):
                    self.__play = False
                    turn = False
                    if (place == Win.DRAW):
                        print('Player ' + str(self.__p1.symbol) + ' and ' + str(self.__p2.symbol) + ' are ' + place)                          
                        break
                    print('Player ' + str(self.__active_player.symbol) + ' wins with a ' + place)  
                    print ("Game Over")                    
                    break 
            except InvalidInputError:
                self.__play = False
                turn = False
                print('Invalid entry error, please select an Integer')  
            finally:
                self.__turn_count = self.__turn_count+1
            
    def place(self, player, old_board):
        return Board.check_board(old_board, (self.__turn_count==(old_board.dims[0]*old_board.dims[1])))

    def game_lobby_loop(self):
            
        while self.__running:
            self.__play=True
            self.__turn_count=1
            self.__ui.display_main_menu()
            user_selection=input()
            try:            
                if re.match('^[1-2]', user_selection):
                    if user_selection == '1':
                        self.game_loop()
                    elif user_selection == '2':
                        print('Exiting')
                        sys.exit()
                else:
                    raise InvalidInputError
            except InvalidInputError:
                print('Invalid data entry error, please try another selection')                
                
    def game_loop(self):
        self.__ui.display_lobby_menu()            
        user_selection=input()
        
        if re.match('^[1-9][0-9]?$|^100$', user_selection):            
            self.__active_board = Board((int(user_selection), int(user_selection)))
        else:
            raise InvalidInputError
            
        while self.__play:
            if self.__active_player == self.__p1:
                self.__active_player = self.__p2
            else:
                self.__active_player = self.__p1
            Board.display_board(self.__active_board.grid)   
            self.turn(self.__active_board)            
            
game = GameState(Player(Sym('X')),Player(Sym('O')))
