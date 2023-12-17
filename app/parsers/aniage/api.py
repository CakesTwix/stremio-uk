from main import app
from fastapi import Depends
from schemas import Manifest, Catalogs

from .settings import settings
from .schemas import Preview, Series, Stream
from .services import (
    get_session,
    get_previews_metadata,
    get_series_metadata,
    get_videos,
    get_streams,
)

import aiohttp


@app.get(f"/{settings.name.lower()}/manifest.json", tags=[settings.name])
def addon_manifest() -> Manifest:
    manifest = Manifest(
        id="ua.cakestwix.stremio.aniage",
        version="1.2.0",
        logo=f"https://www.google.com/s2/favicons?domain={settings.main_url}&sz=128",
        name="Aniage",
        description="Перший нормальний сайт, який зроблено з нуля без використання руснявих технологій.",
        types=["movie", "series"],
        catalogs=[
            Catalogs(
                type=item[1],
                id=f"aniage_{item[0]}",
                name=f"Aniage {item[0]}",
                extra=[{"genres": "anime"}],
            )
            for item in [
                ["Повнометражне", "movie"],
                ["ТБ-Серіал", "series"],
                ["ONA", "series"],
                ["OVA", "series"],
                ["SPECIALS", "series"],
                ["ТБ-Спешл", "series"],
                ["Короткометражне", "movie"],
            ]
        ],
        resources=[
            "catalog",
            "meta",
            "stream",
        ],
    )

    # Search Catalog
    manifest.catalogs.append(
        Catalogs(
            type="series",
            id=f"aniage_search",
            name=f"Aniage Search",
            extra=[{"name": "search", "isRequired": True}],
        )
    )
    # manifest.catalogs[1].extra.append({"name": "search", "isRequired": True})

    return manifest


# Catalog
@app.get("/aniage/catalog/{type_}/aniage_{value}.json", tags=[settings.name])
async def addon_catalog(
    type_: str,
    value: str,
    session: aiohttp.ClientSession = Depends(get_session),
) -> dict[str, list[Preview]]:
    req = {
        "page": 1,
        "pageSize": 28,
        "cleanup": [
            {
                "property": "type",
                "type": "=",
                "value": [
                    value,
                ],
            }
        ],
        "order": {"by": "lastUpdated", "direction": "DESC"},
    }

    async with session.post(settings.latest_url, json=req) as response:
        response_data = (await response.json())["data"]

    return await get_previews_metadata(response_data)


# Pagination
@app.get(
    "/aniage/catalog/{type_}/aniage_{value}/skip={skip}.json", tags=[settings.name]
)
async def addon_catalog_skip(
    value: str,
    skip: int,
    type_: str,
    session: aiohttp.ClientSession = Depends(get_session),
) -> dict[str, list[Preview]]:
    req = {
        "page": (skip / 28) + 1,
        "pageSize": 28,
        "cleanup": [
            {
                "property": "type",
                "type": "=",
                "value": [
                    value,
                ],
            }
        ],
        "order": {"by": "lastUpdated", "direction": "DESC"},
    }
    async with session.post(settings.latest_url, json=req) as response:
        json_content = await response.json()
        if "statusCode" in json_content:
            return {"metas": []}

        response_data = (await response.json())["data"]
        previews_metadata = await get_previews_metadata(response_data, type_)

    return previews_metadata


# Custom Metadata
@app.get("/aniage/meta/{type_}/{id}.json", tags=[settings.name])
async def addon_meta(
    id: str, type_: str, session: aiohttp.ClientSession = Depends(get_session)
) -> dict[str, Series]:
    async with session.get(f"{settings.main_url}/watch?wid={id}") as response:
        series_metadata = await get_series_metadata(
            id,
            await response.text(),
            await get_videos(id, await response.text(), session),
            type_,
        )

    return series_metadata


# Series
@app.get("/aniage/stream/{type_}/{id}/{episode_num}.json", tags=[settings.name])
async def addon_stream(
    id: str, episode_num: int, session: aiohttp.ClientSession = Depends(get_session)
) -> dict[str, list[Stream]]:
    async with session.get(f"{settings.main_url}/watch?wid={id}") as response:
        streams = await get_streams(id, episode_num, session, await response.text())
    return streams


# Search
@app.get(
    "/aniage/catalog/series/aniage_search/search={query}.json", tags=[settings.name]
)
async def addon_search(
    query: str,
    session: aiohttp.ClientSession = Depends(get_session),
) -> dict[str, list[Preview]]:
    async with session.get(f"{settings.finder_url}?query={str(query)}") as response:
        response_data = await response.json()

    return await get_previews_metadata(response_data)
