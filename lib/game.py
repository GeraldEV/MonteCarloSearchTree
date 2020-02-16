import logging
import random

from abc import ABC, abstractmethod


LOGGER = logging.getLogger("game.core")

class Player(ABC):
  PLAYER_1 = 1
  PLAYER_2 = 2

  @staticmethod
  def other(player):
    return 3 - player

  def __init__(self, name):
    self.name = name

  @abstractmethod
  def getMove(self, board):
    pass


class RandomPlayer(Player):
  def getMove(self, board):
    return random.choice(board.getPossibleMoves(self.PLAYER_NUM))


class UserPlayer(Player):
  def getMove(self, board):
    possibleMoves = board.getPossibleMoves(self.PLAYER_NUM)
    move = None

    while move not in possibleMoves:
      try:
        move = int(input(">> "))
      except:
        pass

    return move


class GameStates(object):
  DRAW = -1
  CONTINUE = 0
  PLAYER_1_WIN = 1
  PLAYER_2_WIN = 2


class Game(object):
  def __init__(self, board):
    self.board = board
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
    LOGGER.info("Turn: %s" % activePlayer.name)

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
