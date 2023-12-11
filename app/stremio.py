from fastapi.responses import JSONResponse
from fastapi_stremio import app
from parsers import aniage

LOGO_URL = "https://www.stremio.com/website/stremio-logo-small.png"

MANIFEST = {
    "id": "ua.cakestwix.stremio",
    "version": "1.0.0",
    "logo": LOGO_URL,
    "name": "Українське",
    "description": "Український Stremio-аддон",
    "types": ["movie", "series"],
    "catalogs": [
        {
            "type": "series",
            "id": "aniage",
            "name": "Aniage",
            "extra": [{"genres": "anime"}],
        }
    ],
    "resources": [
        "catalog",
        "meta",
        "stream",
    ],
}


@app.get("/manifest.json", tags=["Base"])
def addon_manifest():
    return JSONResponse(content=MANIFEST)
