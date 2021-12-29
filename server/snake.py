import enum


class Direction(enum.Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class SnakeException(BaseException):
    ...


class PlayerDied(SnakeException):
    ...


class PlayerExited(SnakeException):
    ...


class Snake:
    def __init__(self, rows, cols):
        """
        snakes = {
            133: [(1, 1), (1, 2), (1, 3), (1, 4), (2, 4), (3, 4)],
            ...
        }
        apples = {(1, 2), (34, 22)}
        """
        self.rows = rows
        self.cols = cols
        self.snakes = {}
        self.apples = set([])
        self.board = [[0 for j in range(cols)] for i in range(rows)]

    def move(self, user_id: int, direction: Direction) -> None:
        snake = self.snakes[user_id]

        if (True):
            raise PlayerDied()

        if(True):
            raise PlayerExited()


__all__ = ['Snake']
