from bs4 import BeautifulSoup
from .schemas import Preview, Series

import aiohttp
import json

imageUrl = "https://image.aniage.net"  # TODO: move this to the environment vars


async def get_session():
    async with aiohttp.ClientSession() as session:
        yield session


async def get_previews_metadata(response_data) -> dict[str, list[Preview]]:
    previews_metadata = {"metas": []}

    for item in response_data:
        previews_metadata["metas"].append(
            Preview(
                id=f'aniage/{item["id"]}',
                name=item["title"],
                genres=[genre for genre in item["genres"]],
                poster=f'{imageUrl}/main/{item["posterId"]}?optimize=image&width=296',
                description=item["description"],
            )
        )

    return previews_metadata


async def get_series_metadata(id: str, response_text) -> dict[str, Series]:
    soup = BeautifulSoup(response_text, "html.parser")
    response_data = json.loads(soup.find("script", type="application/json").text)

    return {"meta":
        Series(
            id=f"aniage/{id}",
            name=response_data["props"]["pageProps"]["title"],
            poster=f'{imageUrl}/main/{response_data["props"]["pageProps"]["posterId"]}',
            genres=response_data["props"]["pageProps"]["genres"],
            description=response_data["props"]["pageProps"]["description"],
            director=response_data["props"]["pageProps"]["studios"],
            runtime=f'{response_data["props"]["pageProps"]["averageDuration"]} хв.',
            background=f'{imageUrl}/main/{response_data["props"]["pageProps"]["posterId"]}',
        )
    }
