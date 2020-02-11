import math
import random
import logging

from abc import ABC, abstractmethod

LOGGER = logging.getLogger("game.montecarlo")

INF = math.inf
NEG_INF = -math.inf


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


class GameStates(object):
    DRAW = -1
    CONTINUE = 0
    PLAYER_1_WIN = 1
    PLAYER_2_WIN = 2


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
    def __init__(self, parent, treePlayer, playerTurn, board):
        self.parent = parent
        self.treePlayer = treePlayer

        self.playerTurn = playerTurn

        self.board = board
        self.children = None

        self.nodeValue = None

    def _populateChildren(self):
        self.children = dict()

        for move in self.board.getPossibleMoves(self.playerTurn):
            nextBoard = self.board.copy()
            nextBoard.makeMove(move, self.playerTurn)
            self.children[move] = Node(self, self.treePlayer, Player.other(self.playerTurn), nextBoard)

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
