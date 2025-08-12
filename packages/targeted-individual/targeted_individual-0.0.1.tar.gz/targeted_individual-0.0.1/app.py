import json
from bleak import BleakScanner
from aiohttp import ClientSession


async def devices_generator():
    devices = await BleakScanner.discover()
    for device in devices:
        yield json.dumps({"address": device.address, "name": device.name})


async def fetch(host: str, port: int):
    async with ClientSession() as session:
        response = await session.get(f"http://{host}:{port}")
        return response.text()

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
