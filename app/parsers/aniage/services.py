from bs4 import BeautifulSoup
from .schemas import Preview, Series, Videos
from fastapi import Depends
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


async def get_series_metadata(
    id: str, response_text: str, videos=list[Videos]
) -> dict[str, Series]:
    soup = BeautifulSoup(response_text, "html.parser")
    response_data = json.loads(soup.find("script", type="application/json").text)

    return {
        "meta": Series(
            id=f"aniage/{id}",
            name=response_data["props"]["pageProps"]["title"],
            poster=f'{imageUrl}/main/{response_data["props"]["pageProps"]["posterId"]}',
            genres=response_data["props"]["pageProps"]["genres"],
            description=response_data["props"]["pageProps"]["description"],
            director=response_data["props"]["pageProps"]["studios"],
            runtime=f'{response_data["props"]["pageProps"]["averageDuration"]} хв.',
            background=f'{imageUrl}/main/{response_data["props"]["pageProps"]["posterId"]}',
            videos=videos,
        )
    }


async def get_videos(
    id: str, response_text: str, session: aiohttp.ClientSession
) -> list[Videos]:
    videos = []

    soup = BeautifulSoup(response_text, "html.parser")
    meta_json = json.loads(soup.find("script", type="application/json").text)

    # Getting list voices
    for voice in meta_json["props"]["pageProps"]["teams"]:
        # String build for get voice names
        stringTeam = "https://master.api.aniage.net/anime/teams/by-ids?"
        stringTeam += f"ids={voice['teamId']}&"
        break

    async with session.get(stringTeam) as voiceNames:
        voiceNamesJson = await voiceNames.json()

    index = 0
    for voice in voiceNamesJson:
        # Do list of episodes
        async with session.get(
            f"https://master.api.aniage.net/anime/episodes?animeId={id}&page=1&pageSize=30&sortOrder=ASC&teamId={voice['id']}&volume=1"
        ) as episodes:
            for episode in await episodes.json():
                episodeName = (
                    f"Серія {episode['episodeNum']}"
                    if episode["title"] in [". ", "."]
                    or episode["title"] == episode["episodeNum"]
                    else f"Серія {episode['episodeNum']} - {episode['title']}"
                )

                if episode["videoSource"]:
                    thumbnail = f"https://image.aniage.net/main/{episode['videoSource']['previewPath']}"
                elif episode["playPath"]:
                    thumbnail = (
                        f"https://image.aniage.net/main/{episode['previewPath']}"
                    )
                elif episode["s3VideoSource"]:
                    thumbnail = f"https://image.aniage.net/{episode['s3VideoSource']['previewPath']}"

                videos.append(
                    Videos(
                        id=f'aniage/{episode["animeId"]}/{episode["episodeNum"]}',
                        title=episodeName,
                        thumbnail=thumbnail,
                        released=episode["lastUpdated"],
                        season=episode["volume"],
                        episode=episode["episodeNum"],
                    )
                )

        index += 1

    return videos
