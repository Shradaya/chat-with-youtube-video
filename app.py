import asyncio
from src.run import execute
from src.config import config


if __name__ == "__main__":
    asyncio.run(execute("Chat With Youtube Videos"))
