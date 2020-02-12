import math
import random
import logging

from abc import ABC, abstractmethod
from game import GameStates, Player

LOGGER = logging.getLogger("game.montecarlo")

INF = math.inf
NEG_INF = -math.inf


class Board(ABC):
    @abstractmethod
    def getPossibleMoves(self, player):
        pass

    @abstractmethod
    def getGameState(self):
        pass

    @abstractmethod
    def evaluate(self):
        pass

    @abstractmethod
    def makeMove(self, move, player):
        pass

    @abstractmethod
    def copy(self):
        pass


class Node(object):
    def __init__(self, parent, treePlayer, board):
        self.parent = parent
        self.treePlayer = treePlayer

        self.playerTurn = board.turn

        self.board = board
        self.children = None

        self.nodeValue = None

    def _populateChildren(self):
        self.children = dict()

        for move in self.board.getPossibleMoves(self.playerTurn):
            nextBoard = self.board.copy()
            nextBoard.makeMove(move, self.playerTurn)
            self.children[move] = Node(self, self.treePlayer, nextBoard)

    def evaluateBoard(self):
        boardValue = self.board.evaluate()
        if self.treePlayer == Player.PLAYER_2:
            boardValue *= -1

        return boardValue

    def evaluate(self, currentDepth, maxDepth):
      self.nodeValue = self._evaluate(currentDepth, maxDepth)

    def _evaluate(self, currentDepth, maxDepth):
        boardState = self.board.getGameState()
        if boardState != GameStates.CONTINUE:
            return self.evaluateEndGame(boardState)

        if currentDepth == maxDepth or len(self.board.getPossibleMoves(self.playerTurn)) == 0:
            return self.evaluateBoard()

        if self.children is None:
            self._populateChildren()

        comparison = lambda x, y: x > y
        bestMoveValue = NEG_INF
        if self.playerTurn != self.treePlayer:
            comparison = lambda x, y: x < y
            bestMoveValue = INF

        bestMove = None
        for move in self.children:
            self.children[move].evaluate(currentDepth + 1, maxDepth)
            nodeValue = self.children[move].nodeValue
            if comparison(nodeValue, bestMoveValue):
                bestMove = move
                bestMoveValue = nodeValue

        return bestMoveValue

    def getMove(self, currentDepth, maxDepth):
      if not self.nodeValue:
        self.evaluate(currentDepth, maxDepth)

      bestMoves = [move for move in self.children if self.children[move].nodeValue == self.nodeValue]
      return random.choice(bestMoves)

    def evaluateEndGame(self, boardState):
        if boardState == GameStates.PLAYER_1_WIN:
            return (self.treePlayer == Player.PLAYER_1 and INF) or NEG_INF
        elif boardState == GameStates.PLAYER_2_WIN:
            return (self.treePlayer == Player.PLAYER_2 and INF) or NEG_INF

        return 0


class MonteCarloPlayer(Player):
  def __init__(self, name):
    super().__init__(name)
    self.setMaxDepth(4)

  def setMaxDepth(self, depth):
    self.maxDepth = depth

  def getMove(self, board):
    self.node = Node(None, self.PLAYER_NUM, board)
    move = self.node.getMove(0, self.maxDepth)

    LOGGER.debug("%s believes %s is the best move" % (self.name, move))
    return move
