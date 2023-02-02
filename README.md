# MonteCarloSearchTree

Implementation of Monte Carlo Search Tree for classic board games in Python

## Games

The game class is designed to provide a CLI interface for displaying the state of the game and providing simple inputs to denote each intended move.

### Current Games

Games can be found in the `games` directory.

Noughts and Crosses: https://en.wikipedia.org/wiki/Tic-tac-toe
Kalah implemented to the traditional rules: https://en.wikipedia.org/wiki/Kalah


### Add your own game!

Produce a new sub-class of `Board` (from lib/montecarlo.py).
The rules of the game are defined by valid moves and game states (Player 1 Win, Player 2 Win, Draw or Continue).

Implement the `getGameState` method to return one of the four possible game states based on the rules of your game.
Implement the `getPossibleMoves` method to return a set of all possible moves a player can make given the current board state.
Moves are denoted by integer inputs for the current games but could easily be extended to other definitions (e.g. Chess notation).

Implement the `evaluate` method to return an integer between `INF` and `NEG_INF` which represents the "value" of the board relative to Player 1, where `INF` represents an winning board state for Player 1 (assuming they continue with their current strategy) and `NEG_INF` represents a losing board state for Player 1 (under the same assumption).

