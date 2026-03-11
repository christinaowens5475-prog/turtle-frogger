import asyncio
from src.game import Game

async def main():
    await Game().run()

asyncio.run(main())
