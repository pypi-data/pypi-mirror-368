import websockets, asyncio, random, re
import json as json_module
from .just_funcs import getserver
async def keeping(ws, server: str) -> None:
    """Keep the connection alive by sending periodic messages."""
    while ws.open:
        try:
            await ws.send(f"%xt%{server}%pin%1%<RoundHouseKick>%")
            await asyncio.sleep(60)  # Keep-alive interval
        except websockets.exceptions.ConnectionClosedError:
            print("Connection closed, stopping keep-alive")
            break
