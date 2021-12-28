const ROWS = 75;
const COLS = 100;
const CELL_WIDTH = 10;
const CELL_HEIGHT = 10;

const DEBUG_GAME_SPEED = 100;

const COLOR_APPLE = '#EF476F';
const COLOR_SNAKES = ['#FFD166', '#06D6A0', '#118AB2', '#073B4C'];

type Snake = Array<[number, number]>;

enum Direction {
    UP,
    DOWN,
    LEFT,
    RIGHT
}

class Coordinates {
    x: number;
    y: number;

    constructor (x: number, y: number) {
        this.x = x;
        this.y = y;
    }

    get hash() {
        return `${this.x}_${this.y}`;
    }
}

let board = document.getElementById('board');
let cells = new Map();
let apples = new Map();

let currentDirection = Direction.RIGHT;
let flushedDirection = Direction.RIGHT;

function initBoard() {
    for (let i = 0; i < ROWS; i++) {
        for (let j = 0; j < COLS; j++) {
            let cell = document.createElement('div');
            cell.style.position = 'absolute';
            cell.style.border = '1px solid #eee';
            cell.style.left = j * CELL_WIDTH + 'px';
            cell.style.top = i * CELL_HEIGHT + 'px';
            cell.style.width = CELL_WIDTH + 'px';
            cell.style.height = CELL_HEIGHT + 'px';
            cell.style.backgroundColor = '#fff';
            board.appendChild(cell);
            let coords = new Coordinates(i, j)
            cells.set(coords.hash, cell);
        }
    }
}

function drawApple(coords: Coordinates) {
    let cell = cells.get(coords.hash);
    if (cell !== undefined) {
        cell.style.backgroundColor = COLOR_APPLE;
        cell.style.border = 'none';
        cell.style.borderRadius = '50%';
        apples.set(coords.hash, cell);
    }
}

function initSnakes(snakes: Map<number, Array<Array<number>>>) {
    for(const [snakeID, coords] of snakes) {
        for (let i = 0; i < coords.length; i++) {
            const cellCoords = new Coordinates(coords[i][0], coords[i][1]);
            cells.get(cellCoords.hash).style.backgroundColor = COLOR_SNAKES[snakeID];
        }
    };
}

function clearCell(coords: Coordinates) {
    let cell = cells.get(coords.hash);
    if (cell === undefined) {
        console.log(coords, coords.hash);
    }
    cell.style.backgroundColor = '#fff';
}

function assignCell(coords: Coordinates, snakeID: number) {
    let cell = cells.get(coords.hash);
    cell.style.backgroundColor = COLOR_SNAKES[snakeID];
}

function move(coords: Snake, direction: Direction, snakeID: number): Coordinates {
    // Drop tail
    let coordsTail = new Coordinates(...coords.shift());
    clearCell(coordsTail);

    // Add head
    let [x, y] = coords[coords.length-1];
    switch (direction) {
        case Direction.UP:
            coords.push([x-1, y]);
            flushedDirection = Direction.UP;
            break;
        case Direction.DOWN:
            coords.push([x+1, y]);
            flushedDirection = Direction.DOWN;
            break;
        case Direction.LEFT:
            coords.push([x, y-1]);
            flushedDirection = Direction.LEFT;
            break;
        case Direction.RIGHT:
            coords.push([x, y+1]);
            flushedDirection = Direction.RIGHT;
            break;
    }
    const [newX, newY] = coords[coords.length-1];
    const coordsNewHead = new Coordinates(newX, newY);
    assignCell(coordsNewHead, snakeID);

    return coordsNewHead;
}

window.addEventListener('keydown', (e) => {
    switch (e.key) {
        case 'ArrowUp':
            if (flushedDirection !== Direction.DOWN) {
                currentDirection = Direction.UP;
            }
            break;
        case 'ArrowDown':
            if (flushedDirection !== Direction.UP) {
                currentDirection = Direction.DOWN;
            }
            break;
        case 'ArrowLeft':
            if (flushedDirection !== Direction.RIGHT) {
                currentDirection = Direction.LEFT;
            }
            break;
        case 'ArrowRight':
            if (flushedDirection !== Direction.LEFT) {
                currentDirection = Direction.RIGHT;
            }
            break;
    }
});

const snakes: Map<number, Snake> = new Map([
    [0, [[13, 10], [14, 10], [14, 11], [14, 12]]],
    [1, [[9, 1], [10, 1], [11, 1], [12, 1], [12, 2], [12, 3], [12, 4]]],
]);

initBoard();
initSnakes(snakes);
drawApple(new Coordinates(50, 50));

let test = setInterval(() => {
    move(snakes.get(1), currentDirection, 1);
}, 100);
