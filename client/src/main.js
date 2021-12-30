const ROWS = 75;
const COLS = 100;
const CELL_WIDTH = 10;
const CELL_HEIGHT = 10;
const DEBUG_GAME_SPEED = 100;
const COLOR_APPLE = '#EF476F';
const COLOR_SNAKES = ['#FFD166', '#06D6A0', '#118AB2', '#073B4C'];
var Direction;
(function (Direction) {
    Direction[Direction["UP"] = 0] = "UP";
    Direction[Direction["DOWN"] = 1] = "DOWN";
    Direction[Direction["LEFT"] = 2] = "LEFT";
    Direction[Direction["RIGHT"] = 3] = "RIGHT";
})(Direction || (Direction = {}));
class Coordinates {
    constructor(x, y) {
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
let directionQueue = [];
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
            let coords = new Coordinates(i, j);
            cells.set(coords.hash, cell);
        }
    }
}
function drawApple(coords) {
    let cell = cells.get(coords.hash);
    if (cell !== undefined) {
        cell.style.backgroundColor = COLOR_APPLE;
        cell.style.border = 'none';
        cell.style.borderRadius = '50%';
        apples.set(coords.hash, cell);
    }
}
function initSnakes(snakes) {
    for (const [snakeID, coords] of snakes) {
        for (let i = 0; i < coords.length; i++) {
            const cellCoords = new Coordinates(coords[i][0], coords[i][1]);
            cells.get(cellCoords.hash).style.backgroundColor = COLOR_SNAKES[snakeID];
        }
    }
    ;
}
function clearCell(coords) {
    let cell = cells.get(coords.hash);
    cell.style.backgroundColor = '#fff';
}
function assignCell(coords, snakeID) {
    let cell = cells.get(coords.hash);
    cell.style.backgroundColor = COLOR_SNAKES[snakeID];
}
function compatibleDirections(dir1, dir2) {
    if (dir1 == Direction.UP && dir2 == Direction.DOWN) {
        return false;
    }
    if (dir1 == Direction.DOWN && dir2 == Direction.UP) {
        return false;
    }
    if (dir1 == Direction.LEFT && dir2 == Direction.RIGHT) {
        return false;
    }
    if (dir1 == Direction.RIGHT && dir2 == Direction.LEFT) {
        return false;
    }
    return true;
}
function move(coords, snakeID) {
    let nextDirection;
    while (directionQueue.length > 0) {
        nextDirection = directionQueue.shift();
        if (compatibleDirections(nextDirection, flushedDirection)) {
            currentDirection = nextDirection;
            break;
        }
    }
    let coordsTail = new Coordinates(...coords.shift());
    clearCell(coordsTail);
    let [x, y] = coords[coords.length - 1];
    switch (currentDirection) {
        case Direction.UP:
            coords.push([x - 1, y]);
            break;
        case Direction.DOWN:
            coords.push([x + 1, y]);
            break;
        case Direction.LEFT:
            coords.push([x, y - 1]);
            break;
        case Direction.RIGHT:
            coords.push([x, y + 1]);
            break;
    }
    flushedDirection = currentDirection;
    const [newX, newY] = coords[coords.length - 1];
    const coordsNewHead = new Coordinates(newX, newY);
    assignCell(coordsNewHead, snakeID);
    return coordsNewHead;
}
window.addEventListener('keydown', (e) => {
    switch (e.key) {
        case 'ArrowUp':
        case 'w':
        case 'W':
            directionQueue.push(Direction.UP);
            break;
        case 'ArrowDown':
        case 's':
        case 'S':
            directionQueue.push(Direction.DOWN);
            break;
        case 'ArrowLeft':
        case 'a':
        case 'A':
            directionQueue.push(Direction.LEFT);
            break;
        case 'ArrowRight':
        case 'd':
        case 'D':
            directionQueue.push(Direction.RIGHT);
            break;
    }
});
const snakes = new Map([
    [0, [[13, 10], [14, 10], [14, 11], [14, 12]]],
    [1, [[9, 1], [10, 1], [11, 1], [12, 1], [12, 2], [12, 3], [12, 4]]],
]);
initBoard();
initSnakes(snakes);
let test = setInterval(() => {
    move(snakes.get(1), 1);
}, DEBUG_GAME_SPEED);
//# sourceMappingURL=main.js.map