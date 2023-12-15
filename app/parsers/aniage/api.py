from fastapi_stremio import app
from fastapi import Depends

from .settings import settings
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
    async with session.post(settings.latest_url, json=req) as response:
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
    async with session.post(settings.latest_url, json=req) as response:
        response_data = (await response.json())["data"]
        previews_metadata = await get_previews_metadata(response_data)

    return previews_metadata


# Custom Metadata
@app.get("/meta/series/aniage/{id}.json", tags=["Aniage"])
async def addon_meta(
    id: str, session: aiohttp.ClientSession = Depends(get_session)
) -> dict[str, Series]:
    async with session.get(f"{settings.main_url}/watch?wid={id}") as response:
        series_metadata = await get_series_metadata(
            id,
            await response.text(),
            await get_videos(id, await response.text(), session),
        )

    return series_metadata


# Series
@app.get("/stream/series/aniage/{id}/{episode_num}.json", tags=["Aniage"])
async def addon_stream(
    id: str, episode_num: int,
    session: aiohttp.ClientSession = Depends(get_session)
) -> dict[str, list[Stream]]:
    async with session.get(f"{settings.main_url}/watch?wid={id}") as response:
        streams = await get_streams(
            id, episode_num, session, await response.text()
        )
    return streams
