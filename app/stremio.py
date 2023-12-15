from fastapi.responses import JSONResponse
from fastapi_stremio import app
from parsers.aniage import api
from schemas import Manifest, Catalogs


@app.get("/manifest.json", tags=["Base"])
def aniage_manifest() -> Manifest:
    return Manifest(
        id="ua.cakestwix.stremio",
        version="1.1.0",
        logo="https://www.stremio.com/website/stremio-logo-small.png",
        name="Українське",
        description="Український Stremio-аддон",
        types=["movie", "series"],
        catalogs=[
            Catalogs(
                type="series",
                id="aniage_series",
                name="Aniage Серіали",
                extra=[{"genres": "anime"}],
            ),
        ],
        resources=[
            "catalog",
            "meta",
            "stream",
        ],
    )
