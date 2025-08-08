from dataclasses import dataclass
import numpy as np
from abc import ABC, abstractmethod


@dataclass
class State:
    """basic game state"""

    board: np.ndarray  # game board
    legal: np.ndarray  # mask of leagal moves
    point: int = 0  # how many points have we earned so far
    ended: bool = False  # has the game ended?
    maxim: bool = True  # are we player 1 (maxim) or player 2 (not maxim (minim?))?

    @property
    def minim(self):  # or are we player 2 (minim)?
        return not self.maxim


class Env(ABC):
    """basic environment parent class"""

    @abstractmethod
    def init(self) -> State:
        pass

    @abstractmethod
    def step(self, state, action) -> State:
        pass
