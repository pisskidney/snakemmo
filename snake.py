from __future__ import annotations

import enum
from abc import ABC
from random import choice, randint
from typing import List, Deque, Dict, Any, Tuple
from collections import deque, namedtuple, defaultdict


Cell = namedtuple('Point', ['x', 'y'])


def move_cell(cell: Cell, direction: Direction) -> Cell:
    transform_func = {
        Direction.UP: lambda p: Cell(p.x-1, p.y),
        Direction.DOWN: lambda p: Cell(p.x+1, p.y),
        Direction.LEFT: lambda p: Cell(p.x, p.y-1),
        Direction.RIGHT: lambda p: Cell(p.x, p.y+1),
    }
    func = transform_func[direction]
    return func(cell)


class Collision(ABC):
    ...


class Direction(enum.Enum):
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'


class SnakeGameException(BaseException):
    ...


class PlayerDied(SnakeGameException):
    ...


class PlayerExited(SnakeGameException):
    ...


class Apple():
    ...


class Snake(Collision):
    def __init__(
        self, user_id: int,
        initial_direction: Direction,
        cells: Deque[Cell]
    ):
        self.user_id = user_id
        self.direction = initial_direction
        self.cells = cells
        self.eaten_apples: Deque[Cell] = deque([])

    @property
    def head(self):
        return self.cells[-1]

    @property
    def torso(self):
        return self.cells[len(self.cells) // 2]

    @property
    def tail(self):
        return self.cells[0]

    def is_tail_apple(self):
        return self.eaten_apples and self.eaten_apples[0] == self.tail

    @staticmethod
    def dist(snake1: Snake, snake2: Snake) -> int:
        """
        Get an approximate Marshall distance between two snakes.
        We calculate this by getting the min of the M distance of heads, middle points and tails.

        Optimal should be doing 2 BFS's.
        """

        def marshall_distance(coords1, coords2):
            return abs(coords1[0] - coords2[0]) + abs(coords1[1] - coords2[1])

        return min(
            marshall_distance(snake1.head, snake2.head),
            marshall_distance(snake1.torso, snake2.torso),
            marshall_distance(snake1.tail, snake2.tail),
            marshall_distance(snake1.head, snake2.tail),
            marshall_distance(snake1.tail, snake2.head),
        )

    def move(self) -> Tuple[Cell, Cell]:
        """
        Move the snake cells according to the direction.
        Return the evacuated cells and the newly created ones.
        """
        next_head = move_cell(self.head, self.direction)
        if not self.is_tail_apple():
            tail = self.cells.popleft()
        self.cells.append(next_head)
        return tail, next_head

    def serialize(self) -> List[List[int]]:
        return [[cell.x, cell.y] for cell in self.cells]


class SnakeGame:
    SNAKE_LENGTH_INITIAL = 10
    MAX_APPLES_PER_PLAYER = 15

    def __init__(self, rows: int, cols: int):
        """
        Snake game instance.
        Each session has its own.
        """
        self.rows = rows
        self.cols = cols
        self.snakes: Dict[int, Snake] = {}
        self.apples: List[Cell] = []
        self.inputs: Dict[int, Deque[Direction]] = defaultdict(deque)
        self.board: List[List[Any]] = [[None for j in range(cols)] for i in range(rows)]
        self.dead_last_tick: List[int] = []

    def register_snake(self, user_id: int) -> Snake:
        """
        Find a suitable place on the board to add the snake to.
        Return the Snake instance.
        """
        # @TODO Snake initial position generator is ugly
        snake_cells = deque([])
        direction = choice(list(Direction))
        while len(snake_cells) != self.SNAKE_LENGTH_INITIAL:
            cell = Cell(
                randint(self.SNAKE_LENGTH_INITIAL, self.rows - self.SNAKE_LENGTH_INITIAL),
                randint(self.SNAKE_LENGTH_INITIAL, self.cols - self.SNAKE_LENGTH_INITIAL)
            )
            for _ in range(self.SNAKE_LENGTH_INITIAL):
                if self.board[cell.x][cell.y] is not None:
                    break
                snake_cells.append(cell)
                cell = move_cell(cell, direction)

        snake = Snake(user_id, direction, snake_cells)
        for cell in snake_cells:
            self.board[cell.x][cell.y] = snake
        self.snakes[user_id] = snake
        return snake

    def tick(self) -> None:
        """
        Move all snakes.
        Check for integrity violations (dead snakes).
        """
        self.dead_last_tick = []
        dead = []
        for user_id, snake in self.snakes.items():
            # Find first valid input in the input queue (if it exists)
            while self.inputs.get(user_id):
                candidate_direction = self.inputs.get(user_id).popleft()
                if self.is_valid_input(candidate_direction, snake.direction):
                    snake.direction = candidate_direction
                    break
            tail, head = snake.move()
            if (
                    not (0 <= head.x < self.rows) or
                    not (0 <= head.y < self.cols) or
                    issubclass(type(self.board[head.x][head.y]), Collision)
            ):
                dead.append(user_id)
            else:
                self.board[head.x][head.y] = snake
                self.board[tail.x][tail.y] = None

        # Handle dead snakes
        for user_id in dead:
            self.kill(user_id)

    def is_valid_input(self, new_direction: Direction, current_direction: Direction) -> bool:
        """
        Returns a bool indicating if the new direction is allowed given the current direction.
        """
        if new_direction == Direction.UP and current_direction == Direction.DOWN:
            return False
        if new_direction == Direction.DOWN and current_direction == Direction.UP:
            return False
        if new_direction == Direction.LEFT and current_direction == Direction.RIGHT:
            return False
        if new_direction == Direction.RIGHT and current_direction == Direction.LEFT:
            return False
        return True

    def kill(self, user_id: int) -> None:
        """
        Handle death of a snake.

        1. Add to death list
        2. Transform dead cells into apples
        """
        # Iterate through snake body except head that collided
        self.dead_last_tick.append(user_id)
        for cell in list(self.snakes[user_id].cells)[:-1]:
            apple = Apple()
            self.board[cell.x][cell.y] = apple
            self.apples.append(cell)

            # Remove any commands left in the queue
            if user_id in self.inputs:
                print('here', self.inputs)
                del self.inputs[user_id]
                print('after there', self.inputs)

        del self.snakes[user_id]

    def serialize(self) -> Dict[str, Any]:
        return {
            'snakes': {user_id: snake.serialize() for user_id, snake in self.snakes.items()},
            'apples': [[apple.x, apple.y] for apple in self.apples],
            'deaths': self.dead_last_tick,
        }


__all__ = ['SnakeGame']
