import os
import json
import signal
import asyncio
import structlog
import websockets
from typing import Any, Optional

from .snake import Snake


logger = structlog.get_logger()

SESSIONS = {
    'test': {
        'players': set([]),
        'observers': set([]),
        'game': Snake(75, 100),
    },
}


async def join(websocket: Any, session_id: str, user_id: int):
    logger.info(f'Player {user_id=} joined {session_id=}')

    SESSIONS[session_id]['players'].add(websocket)

    try:
        async for message in websocket:
            ...
    finally:
        SESSIONS[session_id]['players'].remove(websockets)


async def observe(websocket: Any, session_id: str, user_id: Optional[int]):
    logger.info(f'Observer {user_id=} joined {session_id=}')

    SESSIONS[session_id]['observers'].add(websocket)

    try:
        async for message in websocket:
            ...
    finally:
        SESSIONS[session_id]['observers'].remove(websockets)


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


async def main():
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
    port = int(os.environ.get('PORT', 8001))

    logger.info('Server started...')

    async with websockets.serve(handler, '', port):
        await stop


if __name__ == '__main__':
    asyncio.run(main())
