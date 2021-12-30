import os
import json
import signal
import asyncio
import structlog
import websockets
from typing import Any, Optional

from snake import SnakeGame, Direction


logger = structlog.get_logger()

FPS = 10

SESSIONS = {
    'test': {
        'players': set([]),
        'observers': set([]),
        'game': SnakeGame(75, 100),
    },
}


async def join(websocket: Any, session_id: str, user_id: int):
    logger.info(f'Player {user_id=} joined {session_id=}')

    session = SESSIONS[session_id]
    players = session['players']
    game = session['game']

    players.add(websocket)
    game.register_snake(user_id)

    try:
        async for message in websocket:
            logger.warning(f'Got {message=}')
            event = json.loads(message)
            user_id = event['user_id']

            direction = {
                'up': Direction.UP,
                'down': Direction.DOWN,
                'left': Direction.LEFT,
                'right': Direction.RIGHT,
            }.get(event['direction'])

            if direction is None:
                continue

            SESSIONS[session_id]['game'].inputs[user_id].append(direction)
    finally:
        logger.warning(f'Dropped {user_id=}')
        if user_id in game.snakes:
            game.kill(user_id)
        SESSIONS[session_id]['players'].remove(websocket)


async def observe(websocket: Any, session_id: str, user_id: Optional[int]):
    logger.info(f'Observer {user_id=} joined {session_id=}')

    SESSIONS[session_id]['observers'].add(websocket)

    try:
        async for message in websocket:
            ...
    finally:
        SESSIONS[session_id]['observers'].remove(websocket)


async def handler(websocket):
    """
    Assign the client as a player or observer.
    The first message has the format:

    {
        "type": "join" | "observe",
        "session": "session_id",
        "user_id": 1336
    }
    """

    first_message = await websocket.recv()
    event = json.loads(first_message)

    event_type = event['type']
    session_id = event['session_id']
    user_id = event.get('user_id')

    if event_type == 'join':
        await join(websocket, session_id, user_id)
    elif event_type == 'observe':
        await observe(websocket, session_id, user_id)
    elif event_type == 'create':
        ...


def game_loop():
    for session_id, session in SESSIONS.items():
        game = session['game']
        players = session['players']
        game.tick()
        event = {
            'type': 'tick',
        }
        event.update(game.serialize())
        websockets.broadcast(players, json.dumps(event))


async def main():
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
    port = int(os.environ.get('PORT', 8001))

    logger.info('Server started...')

    async with websockets.serve(handler, '', port):
        while not stop.done():
            game_loop()
            await asyncio.sleep(1 / FPS)

    logger.info('Server stopped.')


if __name__ == '__main__':
    asyncio.run(main())
