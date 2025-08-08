from .games import TicTacToe, ConnectFour, Env
from .types import State


def make(game) -> Env:
    match game:
        case "tic_tac_toe":
            return TicTacToe()
        case "connect_four":
            return ConnectFour()
        case _:
            raise ValueError(f"Unknown game: {game}")


__all__ = ["State", "Env", "make"]
