import os
import json
import signal
import uvloop
import asyncio
import structlog
import websockets
from typing import Any, Optional, Dict

from snake import SnakeGame, Direction


logger = structlog.get_logger()

FPS = 15

SESSIONS = {
    'test': {
        'name': 'Test',
        'players': set([]),
        'observers': set([]),
        'game': SnakeGame(50, 100),
        'ranked': False,
        'icon': 'https://i.imgur.com/9dB9PWd.png',
    },
    'forest1': {
        'name': 'Pine Forest',
        'players': set([]),
        'observers': set([]),
        'game': SnakeGame(50, 100),
        'ranked': True,
        'icon': 'https://i.imgur.com/tLyBQWN.png',
    },
    'desert1': {
        'name': 'Arabian Desert',
        'players': set([]),
        'observers': set([]),
        'game': SnakeGame(50, 100),
        'ranked': True,
        'icon': 'https://i.imgur.com/E2kJmpO.png',
    },
    'tropical1': {
        'name': 'Tropical Island',
        'players': set([]),
        'observers': set([]),
        'game': SnakeGame(50, 100),
        'ranked': True,
        'icon': 'https://i.imgur.com/52OxYNa.png',
    },
}


def session_list() -> Dict[Any, Any]:
    return {
        'type': 'session_list',
        'sessions': {
            session_name: {
                'name': session_data['name'],
                'icon': session_data['icon'],
                'players': len(session_data['players']),
                'observers': len(session_data['players']),
            }
            for session_name, session_data in SESSIONS.items()
        }
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
            event = json.loads(message)
            user_id = event['user_id']

            if event['type'] == 'play':
                direction = {
                    'up': Direction.UP,
                    'down': Direction.DOWN,
                    'left': Direction.LEFT,
                    'right': Direction.RIGHT,
                }.get(event['direction'])

                # Disregard non movement keys
                if not direction:
                    continue

                # Only record if snake is alive
                if user_id in game.snakes:
                    SESSIONS[session_id]['game'].inputs[user_id].append(direction)

            elif event['type'] == 'join':
                game.register_snake(user_id)
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
    session_list_message = await websocket.recv()
    event = json.loads(session_list_message)
    event_type = event['type']

    assert event_type == 'session_list'
    await websocket.send(json.dumps(session_list()))

    first_message = await websocket.recv()
    event = json.loads(first_message)

    event_type = event['type']
    session_id = event.get('session_id')
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
    uvloop.install()
    asyncio.run(main())
