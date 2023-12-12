import aiohttp


async def get_session():
    async with aiohttp.ClientSession() as session:
        yield session
