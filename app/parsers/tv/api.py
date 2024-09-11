from fastapi import Depends, HTTPException, APIRouter
from app.schemas import Manifest, Catalogs, Preview, Series, Stream

from .tv_list import meta_tv, catalog_tv
from .stream_list import streams
from .settings import settings
import aiohttp

router = APIRouter(prefix="/tv")

@router.get(f"/{settings.name.lower()}/manifest.json", tags=[settings.name])
def addon_manifest() -> Manifest:
    manifest = Manifest(
        id="ua.cakestwix.stremio.tv",
        version="1.0.0",
        logo="https://cdn6.aptoide.com/imgs/7/5/9/759934acb61ad7914a9fcfa7f26ca76c_icon.png",
        name="Телебачення",
        description="Список телебачення України",
        types=["tv"],
        catalogs=[
            Catalogs(
                type="tv",
                id=f"tv_ua",
                name=f"Телебачення",
                extra=[],
            )
        ],
        resources=["catalog", "meta", "stream"],
    )

    return manifest


# Catalog
@router.get(f"/{settings.name.lower()}/catalog/tv/tv_ua.json", tags=[settings.name])
async def addon_catalog() -> dict[str, list[Preview]]:
    return {"metas": catalog_tv}


# Metadata
@router.get("/tvua/meta/tv/{id}.json", tags=[settings.name])
async def addon_meta(id: str) -> dict[str, Series]:
    if id not in meta_tv:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"meta": meta_tv[id]}


# Stream
@router.get("/tvua/stream/tv/{id}.json", tags=[settings.name])
async def addon_stream(id: str) -> dict[str, list[Stream]]:
    if id not in streams:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"streams": streams[id]}
