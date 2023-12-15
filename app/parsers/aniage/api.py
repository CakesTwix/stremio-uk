from fastapi_stremio import app
from fastapi import Depends

from .schemas import Preview, Series, Stream
from .services import (
    get_session,
    get_previews_metadata,
    get_series_metadata,
    get_videos,
    get_streams
)

import aiohttp
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
    id: str, episodeNum: int,
    session: aiohttp.ClientSession = Depends(get_session)
) -> dict[str, list[Stream]]:
    async with session.get(f"{mainUrl}/watch?wid={id}") as response:
        streams = await get_streams(
            id, episodeNum, session, await response.text()
        )
    return streams
