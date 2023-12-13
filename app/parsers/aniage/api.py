from fastapi_stremio import app
from fastapi.responses import JSONResponse
from fastapi import Depends
from bs4 import BeautifulSoup

from .schemas import Preview, Series
from .services import (
    get_session,
    get_previews_metadata,
    get_series_metadata,
    get_videos,
)

import aiohttp
import json
import logging

logger = logging.getLogger(__name__)

mainUrl = "https://aniage.net"
apiUrl = "https://master.api.aniage.net"
latestUrl = f"{apiUrl}/v2/anime/find"
imageUrl = "https://image.aniage.net"
videoCdn = "https://aniage-video-stream.b-cdn.net/"


# Catalog
@app.get("/catalog/series/aniage.json", tags=["Aniage"])
async def addon_catalog(
    session: aiohttp.ClientSession = Depends(get_session),
) -> dict[str, list[Preview]]:
    req = {
        "page": 1,
        "pageSize": 28,
        "cleanup": [],
        "order": {"by": "lastUpdated", "direction": "DESC"},
    }
    async with session.post(latestUrl, json=req) as response:
        response_data = (await response.json())["data"]
        previews_metadata = await get_previews_metadata(response_data)

    return previews_metadata


# Pagination
@app.get("/catalog/series/aniage/skip={skip}.json", tags=["Aniage"])
async def addon_catalog_skip(
    skip: int, session: aiohttp.ClientSession = Depends(get_session)
) -> dict[str, list[Preview]]:
    req = {
        "page": (skip / 28) + 1,
        "pageSize": 28,
        "cleanup": [],
        "order": {"by": "lastUpdated", "direction": "DESC"},
    }
    async with session.post(latestUrl, json=req) as response:
        response_data = (await response.json())["data"]
        previews_metadata = await get_previews_metadata(response_data)

    return previews_metadata


# Custom Metadata
@app.get("/meta/series/aniage/{id}.json", tags=["Aniage"])
async def addon_meta(
    id: str, session: aiohttp.ClientSession = Depends(get_session)
) -> dict[str, Series]:
    async with session.get(f"{mainUrl}/watch?wid={id}") as response:
        series_metadata = await get_series_metadata(
            id,
            await response.text(),
            await get_videos(id, await response.text(), session),
        )

    return series_metadata


# Series
@app.get("/stream/series/aniage/{id}/{episodeNum}.json", tags=["Aniage"])
async def addon_stream(
    id: str, episodeNum: int, session: aiohttp.ClientSession = Depends(get_session)
):
    streams = {"streams": []}

    async with session.get(f"{mainUrl}/watch?wid={id}") as response:
        soup = BeautifulSoup(await response.text(), "html.parser")
        meta_json = json.loads(soup.find("script", type="application/json").text)

        stringTeam = f"{apiUrl}/anime/teams/by-ids?"
        # Getting list voices
        for voice in meta_json["props"]["pageProps"]["teams"]:
            # String build for get voice names
            stringTeam += f"ids={voice['teamId']}&"

        async with session.get(stringTeam) as voiceNames:
            voiceNamesJson = await voiceNames.json()

        index = 0
        for voice in voiceNamesJson:
            # Do list of episodes
            async with session.get(
                f"{apiUrl}/anime/episodes?animeId={id}&page=1&pageSize=30&sortOrder=ASC&teamId={voice['id']}&volume=1"
            ) as episodes:
                for episode in await episodes.json():
                    if int(episode["episodeNum"]) != episodeNum:
                        continue

                    episodeName = (
                        f"Серія {episode['episodeNum']}"
                        if episode["title"] in [". ", "."]
                        or episode["title"] == episode["episodeNum"]
                        else f"Серія {episode['episodeNum']} - {episode['title']}"
                    )

                    url = None
                    if episode["playPath"]:
                        async with session.get(episode["playPath"]) as video:
                            video_soup = BeautifulSoup(
                                await video.text(), "html.parser"
                            )
                            url = video_soup.find("source")["src"]

                    elif episode["s3VideoSource"]:
                        url = f"{videoCdn}{episode['s3VideoSource']['playlistPath']}"

                    elif episode["videoSource"]:
                        async with session.get(
                            episode["videoSource"]["playPath"]
                        ) as video:
                            video_soup = BeautifulSoup(
                                await video.text(), "html.parser"
                            )
                            url = video_soup.find("source")["src"]

                    streams["streams"].append(
                        {
                            "name": voiceNamesJson[index]["name"],
                            "url": url,
                        }
                    )

            index += 1

    return JSONResponse(content=streams)
