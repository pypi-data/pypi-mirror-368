import os
import sys
import asyncio

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")

from pyipx800v3_async.pyipx800v3_async import IPX800V3, Input, Analog, Output

async def test():
    ipx = IPX800V3(host=os.getenv('IPX800_HOST'), username=os.getenv('IPX800_USER'), password=os.getenv('IPX800_PASS'))
    an1 = Analog(ipx=ipx, id=1)
    print(await an1.status)
    print(await an1)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(test())
    finally:
        loop.stop()