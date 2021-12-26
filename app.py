#!/usr/bin/env python

import json
import asyncio
import structlog
import itertools
import websockets

from connect4 import PLAYER1, PLAYER2, Connect4


logger = structlog.get_logger()


async def handler(websocket):
    game = Connect4()
    turn = itertools.cycle([PLAYER1, PLAYER2])
    player = next(turn)

    async for message in websocket:
        logger.info(f'Reveived {message}')
        event = json.loads(message)

        try:
            game.play(player, event['column'])
        except RuntimeError:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'Wrong move buddy boy!'
            }))
            logger.info(f'{game.last_player} played a wrong move!')

        await websocket.send(json.dumps({
            'type': 'play',
            'player': game.last_player,
            'column': event['column'],
            'row': game.top[event['column']] - 1,
        }))

        if game.last_player_won:
            await websocket.send(json.dumps({
                'type': 'win',
                'player': game.last_player,
            }))
            logger.info(f'{game.last_player} won!')
            break

        player = next(turn)


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
