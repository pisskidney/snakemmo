#!/usr/bin/env python

import json
import secrets
import asyncio
import structlog
import websockets

from connect4 import Connect4, PLAYER1, PLAYER2


logger = structlog.get_logger()

JOIN = {}


async def error(websocket, message):
    event = {
        'type': 'error',
        'message': message,
    }
    await websocket.send(json.dumps(event))


async def start(websocket):
    game = Connect4()
    connected = {websocket}

    join_key = secrets.token_urlsafe(6)
    JOIN[join_key] = game, connected

    try:
        # Send the token to the first client, so that it can construct the join link
        event = {
            'type': 'init',
            'join': join_key,
        }
        await websocket.send(json.dumps(event))
        logger.debug(f'The first player started {id(game)=}')

        async for message in websocket:
            logger.debug(f'First player sent: {message}')
            await move(connected, websocket, game, PLAYER1, message)

    finally:
        del JOIN[join_key]


async def join(websocket, join_key):
    game, connected = JOIN[join_key]
    connected.add(websocket)
    try:
        logger.debug(f'second player joined the game! {id(game)=}')
        async for message in websocket:
            logger.debug(f'second player got message {message}')
            await move(connected, websocket, game, PLAYER2, message)
    finally:
        connected.remove(websocket)


async def observe(websocket, join_key):
    game, connected = JOIN[join_key]
    connected.add(websocket)
    try:
        logger.debug(f'observer joined the game! {id(game)=}')
        async for message in websocket:
            logger.debug(f'observer got message {message}')
    finally:
        connected.remove(websocket)


async def move(connected, websocket, game, player, message):
    to_move = PLAYER2 if game.last_player == PLAYER1 else PLAYER1

    if to_move != player:
        event = {
            'type': 'error',
            'message': 'It is not your turn!',
        }
        await websocket.send(json.dumps(event))
        return

    event = json.loads(message)

    try:
        game.play(player, event['column'])
    except RuntimeError:
        event = {
            'type': 'error',
            'message': 'Wrong move buddy!',
        }
        await websocket.send(json.dumps(event))
        return

    event = {
        'type': 'play',
        'player': game.last_player,
        'column': event['column'],
        'row': game.top[event['column']] - 1,
    }
    websockets.broadcast(connected, event)
    logger.debug(f'broadcast {event}')

    if game.last_player_won:
        event = {
            'type': 'win',
            'player': game.last_player,
        }
        await websocket.send(json.dumps(event))


async def handler(websocket, path):
    # Receive and parse the init event from the client
    message = await websocket.recv()
    event = json.loads(message)
    assert event['type'] == 'init'

    if 'join' in event:
        try:
            _, connected = JOIN[event['join']]
        except KeyError:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'Wrong game ID',
            }))
            return
        if len(connected) == 2:
            # Observer joined
            await observe(websocket, event['join'])
        else:
            # Second player joins game
            await join(websocket, event['join'])
    else:
        # First player starts a new game
        await start(websocket)


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
