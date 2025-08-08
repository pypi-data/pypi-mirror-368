# games.py
#   aigs games
# by: Noah Syrkis

# imports
from aigs.types import State, Env
import numpy as np


# ConnectFour
class ConnectFour(Env):
    def init(self) -> State:
        raise NotImplementedError()  # You should implement this method

    def step(self, state, action) -> State:
        raise NotImplementedError()  # You should implement this method


# TicTacToe
class TicTacToe(Env):
    def init(self) -> State:
        board = np.zeros((3, 3), dtype=np.int8)
        legal = board.flatten() == 0
        state = State(board=board, legal=legal)
        return state

    def step(self, state, action) -> State:
        # make your move
        board = state.board.copy()
        board[action // 3, action % 3] = True

        # did it win?
        winner: bool = (
            board.all(axis=1).any()  # |
            or board.all(axis=0).any()  # —
            or board.trace() == 3  # \
            or np.fliplr(board).trace() == 3  # /
        )

        # is the game over?
        ended = (board != 0).all() | winner

        # return the next state
        return State(
            board=board,
            legal=board.flatten() == 0,  # empty board positions
            ended=ended,
            point=(1 if state.maxim else -1) if winner else 0,
            maxim=not state.maxim,
        )
