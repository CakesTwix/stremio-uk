from fastapi_stremio import app
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
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
async def addon_catalog():
    req = {
        "page": 1,
        "pageSize": 28,
        "cleanup": [],
        "order": {"by": "lastUpdated", "direction": "DESC"},
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(latestUrl, json=req) as response:
            metaPreviews = {
                "metas": [
                    {
                        "id": f'aniage/{item["id"]}',
                        "type": "series",
                        "name": item["title"],
                        "genres": [genre for genre in item["genres"]],
                        "poster": f'{imageUrl}/main/{item["posterId"]}?optimize=image&width=296',
                        "description": item["description"],
                    }
                    for item in (await response.json())["data"]
                ]
            }

    return JSONResponse(content=metaPreviews)

# Pagination
@app.get("/catalog/series/aniage/skip={skip}.json", tags=["Aniage"])
async def addon_catalog_skip(skip: int):
    req = {
        "page": (skip / 28) + 1,
        "pageSize": 28,
        "cleanup": [],
        "order": {"by": "lastUpdated", "direction": "DESC"},
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(latestUrl, json=req) as response:
            metaPreviews = {
                "metas": [
                    {
                        "id": f'aniage/{item["id"]}',
                        "type": "series",
                        "name": item["title"],
                        "genres": [genre for genre in item["genres"]],
                        "poster": f'{imageUrl}/main/{item["posterId"]}?optimize=image&width=296',
                        "description": item["description"],
                    }
                    for item in (await response.json())["data"]
                ]
            }

    return JSONResponse(content=metaPreviews)

# Custom Metadata
@app.get("/meta/series/aniage/{id}.json", tags=["Aniage"])
async def addon_meta(id: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{mainUrl}/watch?wid={id}") as response:
            soup = BeautifulSoup (await response.text(), 'html.parser')
            meta_json = json.loads(soup.find("script", type="application/json").text)

            meta = {
                "meta": {
                    "id": f'aniage/{id}',
                    "type": "series",
                    "name": meta_json["props"]["pageProps"]["title"],
                    "poster": f'{imageUrl}/main/{meta_json["props"]["pageProps"]["posterId"]}',
                    "genres": meta_json["props"]["pageProps"]["genres"],
                    "description": meta_json["props"]["pageProps"]["description"],
                    "director": meta_json["props"]["pageProps"]["studios"],
                    "runtime": f'{meta_json["props"]["pageProps"]["averageDuration"]} хв.',
                    "background": f'{imageUrl}/main/{meta_json["props"]["pageProps"]["posterId"]}',
                }
            }

    return JSONResponse(content=meta)

# Series
@app.get("/stream/series/aniage/{id}.json", tags=["Aniage"])
async def addon_stream(id: str):
    streams = {
        "streams": []
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{mainUrl}/watch?wid={id}") as response:
            soup = BeautifulSoup (await response.text(), 'html.parser')
            meta_json = json.loads(soup.find("script", type="application/json").text)
            
            

            # Getting list voices
            for voice in meta_json["props"]["pageProps"]["teams"]:

                # String build for get voice names
                stringTeam = f"{apiUrl}/anime/teams/by-ids?"
                stringTeam += f"ids={voice['teamId']}&"
                async with session.get(stringTeam) as voiceNames:
                    voiceNamesJson = await voiceNames.json()

                # Do list of episodes
                async with session.get(f"{apiUrl}/anime/episodes?animeId={id}&page=1&pageSize=30&sortOrder=ASC&teamId={voice['teamId']}&volume=1") as episodes:
                    index = 0
                    for episode in await episodes.json():
                        episodeName = f"Серія {episode['episodeNum']}" if episode["title"] in [". ", "."] or episode["title"] == episode["episodeNum"] else f"Серія {episode['episodeNum']} - {episode['title']}"
                        
                        url = None
                        if episode["playPath"]:
                            async with session.get(episode["playPath"]) as video:
                                video_soup = BeautifulSoup (await video.text(), 'html.parser')
                                url = video_soup.find("source")["src"]
                            
                        elif episode["s3VideoSource"]:
                            url = f"{videoCdn}{episode['s3VideoSource']['playlistPath']}"

                        elif episode["videoSource"]:
                            async with session.get(episode["videoSource"]["playPath"]) as video:
                                video_soup = BeautifulSoup (await video.text(), 'html.parser')
                                url = video_soup.find("source")["src"]
                        
                        streams["streams"].append(
                            {
                                "name": episodeName,
                                "url": url,
                                "description": voiceNamesJson[index]["name"]
                            }
                        )       
                
                index += 1       
                    

    return JSONResponse(content=streams)
