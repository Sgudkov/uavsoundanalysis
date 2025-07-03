import json
import asyncio
from websockets.asyncio.client import connect


async def hello():
    async with connect("ws://localhost:8000/ws/") as websocket:
        await websocket.send(json.dumps({"action": "change_color", "id": 1, "color": "red"}))


asyncio.run(hello())
