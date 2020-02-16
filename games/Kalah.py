import logging
import copy

from montecarlo import INF, NEG_INF, Board, MonteCarloPlayer
from game import Game, Player, RandomPlayer, UserPlayer, GameStates


LOGGER = logging.getLogger("game")

def setupStdoutLogger(level=logging.DEBUG):
  LOGGER.setLevel(level)

  ch = logging.StreamHandler()
  ch.setLevel(level)
  formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%H:%M:%S")
  ch.setFormatter(formatter)
  LOGGER.addHandler(ch)


class KalahBoard(Board):
  def __init__(self, houses, seeds):
    self.houses = houses
    self.seeds = seeds

  def copy(self):
    copyBoard = KalahBoard(self.houses, self.seeds)
    copyBoard.contents = copy.deepcopy(self.contents)
    copyBoard.stores = copy.deepcopy(self.stores)
    copyBoard.turn = self.turn

    return copyBoard

  def getGameState(self):
    sumHouses = (sum(self.contents[Player.PLAYER_1]), sum(self.contents[Player.PLAYER_2]))
    if sumHouses[0] == 0 or sumHouses[1] == 0:
      self.stores[Player.PLAYER_1] += sumHouses[0]
      self.stores[Player.PLAYER_2] += sumHouses[1]
      self.contents[Player.PLAYER_1] = [0 for i in range(self.houses)]
      self.contents[Player.PLAYER_2] = [0 for i in range(self.houses)]
    else:
      return GameStates.CONTINUE

    if self.stores[Player.PLAYER_1] > self.stores[Player.PLAYER_2]:
      return GameStates.PLAYER_1_WIN
    elif self.stores[Player.PLAYER_1] < self.stores[Player.PLAYER_2]:
      return GameStates.PLAYER_2_WIN

    assert self.stores[Player.PLAYER_1] == self.stores[Player.PLAYER_2]
    return GameStates.DRAW

  def getPossibleMoves(self, player):
    contents = self.contents[player]
    return [i + 1 for i in range(len(contents)) if contents[i] != 0]

  def makeMove(self, move, player):
    assert player == self.turn
    assert move in self.getPossibleMoves(player)

    move = move - 1
    seeds = self.contents[player][move]
    self.contents[player][move] = 0
    currentPlayer = player
    currentHouse = move - 1

    while seeds > 1:
      if currentHouse < 0:
        if currentPlayer == self.turn:
          self.stores[currentPlayer] += 1
          seeds -= 1

        currentPlayer = Player.other(currentPlayer)
        currentHouse = self.houses - 1
        continue

      self.contents[currentPlayer][currentHouse] += 1
      seeds -= 1
      currentHouse -= 1

    if currentHouse < 0 and currentPlayer == self.turn:
      self.stores[currentPlayer] += 1
      return

    if currentHouse < 0:
      currentPlayer = Player.other(currentPlayer)
      currentHouse = self.houses - 1

    self.contents[currentPlayer][currentHouse] += 1

    mirrorHouse = (self.houses - 1) - currentHouse
    if currentPlayer == self.turn and self.contents[currentPlayer][currentHouse] == 1 and self.contents[Player.other(currentPlayer)][mirrorHouse] != 0:
      self.stores[currentPlayer] += self.contents[currentPlayer][currentHouse]
      self.stores[currentPlayer] += self.contents[Player.other(currentPlayer)][mirrorHouse]
      self.contents[currentPlayer][currentHouse] = 0
      self.contents[Player.other(currentPlayer)][mirrorHouse] = 0

    self.turn = Player.other(self.turn)

  def reset(self):
    self.contents = {Player.PLAYER_1: [self.seeds for x in range(self.houses)], Player.PLAYER_2: [self.seeds for x in range(self.houses)]}
    self.stores = { Player.PLAYER_1: 0, Player.PLAYER_2: 0 }

    self.turn = Player.PLAYER_1

  def prettyPrint(self):
    outputLine = "    "
    for i in range(self.houses):
      outputLine += "|  %2d  " % self.contents[Player.PLAYER_2][i]
    outputLine += "|"

    LOGGER.info(outputLine)

    outputLine = " %2d " + ("|      " * self.houses) + "| %2d"
    outputLine = outputLine % (self.stores[Player.PLAYER_2], self.stores[Player.PLAYER_1])
    LOGGER.info(outputLine)

    outputLine = "    "
    for i in range(self.houses):
      outputLine += "|  %2d  " % self.contents[Player.PLAYER_1][(self.houses - 1) - i]
    outputLine += "|\n"

    LOGGER.info(outputLine)


def evaluateBoard(board):
  gameState = board.getGameState()
  if gameState == GameStates.PLAYER_1_WIN:
    return INF
  elif gameState == GameStates.PLAYER_2_WIN:
    return NEG_INF
  elif gameState == GameStates.DRAW:
    return 0

  p1score = board.stores[Player.PLAYER_1]
  p2score = board.stores[Player.PLAYER_2]

  for house in range(len(board.contents[Player.PLAYER_1])):
    if board.contents[Player.PLAYER_1][house] == house + 1:
      p1score += 1

  for house in range(len(board.contents[Player.PLAYER_2])):
    if board.contents[Player.PLAYER_2][house] == house + 1:
      p2score += 1

  return p1score - p2score


if __name__ == "__main__":
  setupStdoutLogger()

  game = Game(KalahBoard(6, 4))

  userPlayer = UserPlayer("Gerald")
  game.setPlayer(userPlayer, Player.PLAYER_1)

  montePlayer = MonteCarloPlayer("Monty", evaluateBoard)
  game.setPlayer(montePlayer, Player.PLAYER_2)

  game.playGame()

