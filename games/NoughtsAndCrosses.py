import random
import logging
import copy

from montecarlo import INF, NEG_INF, Player, GameStates, Board, Node


LOGGER = logging.getLogger("game")

def setupStdoutLogger(level=logging.DEBUG):
  LOGGER.setLevel(logging.DEBUG)

  ch = logging.StreamHandler()
  ch.setLevel(level)
  formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%H:%M:%S")
  ch.setFormatter(formatter)
  LOGGER.addHandler(ch)


EMPTY = 0

class NACBoard(Board):
  PLAYER_1_PIECE = "O"
  PLAYER_2_PIECE = "X"

  WINNING_SETS = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 4, 8),
    (2, 4, 6),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8))

  def copy(self):
    return copy.deepcopy(self)

  def evaluate(self):
    state = self.getGameState()
    if state == GameStates.PLAYER_1_WIN:
      return INF
    if state == GameStates.PLAYER_2_WIN:
      return NEG_INF
    if state == GameStates.DRAW:
      return 0

    player1Score = 0
    player2Score = 0
    for winningSet in NACBoard.WINNING_SETS:
      elements = [self.contents[element] for element in winningSet]
      if all(map(lambda x: x != Player.PLAYER_2, elements)):
        player1Score += elements.count(Player.PLAYER_1) + 1
      if all(map(lambda x: x != Player.PLAYER_1, elements)):
        player2Score += elements.count(Player.PLAYER_2) + 1

    return player1Score - player2Score

  def getGameState(self):
    for winningSet in NACBoard.WINNING_SETS:
      elements = [self.contents[element] for element in winningSet]
      if elements[0] != EMPTY and elements[0] == elements[1] and elements[1] == elements[2]:
        if elements[0] == Player.PLAYER_1:
          return GameStates.PLAYER_1_WIN
        else:
          return GameStates.PLAYER_2_WIN
    
    if self.contents.count(EMPTY) == 0:
      return GameStates.DRAW

    return GameStates.CONTINUE

  def getPossibleMoves(self, player):
    return [move for move in range(len(self.contents)) if self.contents[move] == EMPTY]

  def makeMove(self, move, player):
    assert player == self.turn

    if self.contents[move] == EMPTY:
      self.contents[move] = player
      self.turn = Player.other(self.turn)


  def reset(self):
    LOGGER.info("Reset board")
    self.contents = [0 for i in range(9)]
    self.turn = Player.PLAYER_1

  def prettyPrint(self):
    output = "\n {0} | {1} | {2}\n---+---+---\n {3} | {4} | {5}\n---+---+---\n {6} | {7} | {8}\n\n"
    output = output.format(*self.__getStringPieces())
    LOGGER.info(output)

  def __getStringPieces(self):
    return [self.__getStringPiece(piece) for piece in self.contents]

  def __getStringPiece(self, piece):
    if piece == EMPTY:
      return " "
    if piece == Player.PLAYER_1:
      return NACBoard.PLAYER_1_PIECE
    if piece == Player.PLAYER_2:
      return NACBoard.PLAYER_2_PIECE
    return "!"


class Game(object):
  def __init__(self):
    self.board = NACBoard()
    self.player1 = None
    self.player2 = None

  def setPlayer(self, player, playerIdentifier):
    player.PLAYER_NUM = playerIdentifier

    if playerIdentifier == Player.PLAYER_1:
      self.player1 = player
    elif playerIdentifier == Player.PLAYER_2:
      self.player2 = player

  def _processOneTurn(self):
    activePlayer = self.player1 if self.board.turn == Player.PLAYER_1 else self.player2

    self.board.prettyPrint()
    move = activePlayer.getMove(self.board)
    self.board.makeMove(move, activePlayer.PLAYER_NUM)

  def playGame(self):
    assert self.player1 is not None
    assert self.player2 is not None

    self.board.reset()

    gameState = self.board.getGameState()
    while gameState == GameStates.CONTINUE:
      self._processOneTurn()
      gameState = self.board.getGameState()

    self.announceResult(gameState)

  def announceResult(self, state):
    self.board.prettyPrint()
    LOGGER.info("The game is over.")
    if state == GameStates.PLAYER_1_WIN:
      LOGGER.info("Player 1 wins! Well Done %s." % self.player1.name)
    elif state == GameStates.PLAYER_2_WIN:
      LOGGER.info("Player 2 wins! Well Done %s." % self.player2.name)
    else:
      LOGGER.info("Game ended in a draw.")


class MonteCarloPlayer(Player):
  def __init__(self, name):
    super().__init__(name)
    
    self.maxDepth = 4

  def setMaxDepth(self, depth):
    self.maxDepth = depth

  def getMove(self, board):
    self.node = Node(None, self.PLAYER_NUM, board.turn, board)
    move = self.node.getMove(0, self.maxDepth)

    LOGGER.info("%s believes %s is the best move" % (self.name, move))
    return move


class RandomPlayer(Player):
  def getMove(self, board):
    return random.choice(board.getPossibleMoves(self.PLAYER_NUM))


class UserPlayer(Player):
  def getMove(self, board):
    possiblePositions = board.getPossibleMoves(self.PLAYER_NUM)
    move = None

    while move not in possiblePositions:
        try:
            move = int(input(">> "))
        except:
            pass

    return move


if __name__ == "__main__":
  setupStdoutLogger()

  game = Game()

  monteCarloPlayer = MonteCarloPlayer("Monty")
  game.setPlayer(monteCarloPlayer, Player.PLAYER_1)

  userPlayer = UserPlayer("Gerald")
  game.setPlayer(userPlayer, Player.PLAYER_2)
  game.playGame()
