import asyncio

from app.bot.main import start_bot


async def main():
    asyncio.run(start_bot())


if __name__ == "__main__":
    asyncio.run(main())
