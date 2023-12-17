from bs4 import BeautifulSoup
from schemas import Manifest, Catalogs, Preview, Series, Stream, Videos
from .settings import settings

import aiohttp
import json
from .utils import get_type


async def get_session():
    async with aiohttp.ClientSession() as session:
        yield session


async def get_previews_metadata(response_data) -> dict[str, list[Preview]]:
    previews_metadata = {"metas": []}

    for item in response_data:
        previews_metadata["metas"].append(
            Preview(
                id=f'{item["id"]}',
                type=get_type(item["type"]),
                name=item["title"],
                genres=[genre for genre in item["genres"]],
                poster=f'{settings.image_url}/main/{item["posterId"]}?optimize=image&width=296',
                description=item["description"],
            )
        )

    return previews_metadata


async def get_series_metadata(
    id: str, response_text: str, videos: list[Videos], type_title: str
) -> dict[str, Series]:
    soup = BeautifulSoup(response_text, "html.parser")
    response_data = json.loads(soup.find("script", type="application/json").text)

    return {
        "meta": Series(
            id=f"{id}",
            type=type_title,
            name=response_data["props"]["pageProps"]["title"],
            poster=f'{settings.image_url}/main/{response_data["props"]["pageProps"]["posterId"]}',
            genres=response_data["props"]["pageProps"]["genres"],
            description=response_data["props"]["pageProps"]["description"],
            director=response_data["props"]["pageProps"]["studios"],
            runtime=f'{response_data["props"]["pageProps"]["averageDuration"]} хв.',
            background=f'{settings.image_url}/main/{response_data["props"]["pageProps"]["posterId"]}',
            videos=videos,
        )
    }


async def get_videos(
    id: str, response_text: str, session: aiohttp.ClientSession
) -> list[Videos]:
    videos = []

    soup = BeautifulSoup(response_text, "html.parser")
    response_data = json.loads(soup.find("script", type="application/json").text)

    if response_data["props"]["pageProps"]["teams"] == []:
        return videos

    string_team = f"{settings.api_url}/anime/teams/by-ids?ids={response_data['props']['pageProps']['teams'][0]['teamId']}"

    async with session.get(string_team) as response:
        voice_names = await response.json()

    # Do list of episodes
    page = 1
    while int(response_data["props"]["pageProps"]["episodes"]) > 0:
        async with session.get(
            f"{settings.api_url}/anime/episodes?animeId={id}&page={page}&pageSize={settings.page_size}&sortOrder=ASC&teamId={voice_names[0]['id']}&volume=1"
        ) as episodes:
            for episode in await episodes.json():
                episode_name = (
                    f"Серія {episode['episodeNum']}"
                    if episode["title"] in [". ", "."]
                    or episode["title"] == episode["episodeNum"]
                    or episode["title"].isdigit()
                    else f"Серія {episode['episodeNum']} - {episode['title']}"
                )

                if episode["videoSource"]:
                    thumbnail = f"{settings.image_url}/main/{episode['videoSource']['previewPath']}"
                elif episode["playPath"]:
                    thumbnail = f"{settings.image_url}/main/{episode['previewPath']}"
                elif episode["s3VideoSource"]:
                    thumbnail = f"{settings.image_url}/{episode['s3VideoSource']['previewPath']}"

                videos.append(
                    Videos(
                        id=f'{episode["animeId"]}/{episode["episodeNum"]}',
                        title=episode_name,
                        thumbnail=thumbnail,
                        released=episode["lastUpdated"],
                        season=episode["volume"],
                        episode=episode["episodeNum"],
                    )
                )

            response_data["props"]["pageProps"]["episodes"] -= settings.page_size
            page += 1

    return videos


async def get_streams(
    id: str, episode_num: int, session: aiohttp.ClientSession, response_text
) -> dict[str, list[Stream]]:
    streams = {"streams": []}

    soup = BeautifulSoup(response_text, "html.parser")
    response_data = json.loads(soup.find("script", type="application/json").text)

    string_team = f"{settings.api_url}/anime/teams/by-ids?"
    # Getting list voices
    for voice in response_data["props"]["pageProps"]["teams"]:
        # String build for get voice names
        string_team += f"ids={voice['teamId']}&"

    async with session.get(string_team) as response:
        voice_names = await response.json()

    # Index for voice names
    index = 0
    for voice in voice_names:
        # Pagination
        page = 1
        episode_count = int(response_data["props"]["pageProps"]["episodes"])
        while episode_count > 0:
            # Get 100 episodes
            async with session.get(
                f"{settings.api_url}/anime/episodes?animeId={id}&page={page}&pageSize={settings.page_size}&sortOrder=ASC&teamId={voice['id']}&volume=1"
            ) as episodes:
                # Parsing, add to streams
                for episode in await episodes.json():
                    # If no episodeNum - drop
                    if int(episode["episodeNum"]) != episode_num:
                        continue

                    # Do cool naming for episode
                    episode_name = (
                        f"Серія {episode['episodeNum']}"
                        if episode["title"] in [". ", "."]
                        or episode["title"] == episode["episodeNum"]
                        or episode["title"].isdigit()
                        else f"Серія {episode['episodeNum']} - {episode['title']}"
                    )

                    # Parsing m3u url
                    url = None
                    if episode["playPath"]:
                        async with session.get(episode["playPath"]) as video:
                            video_soup = BeautifulSoup(
                                await video.text(), "html.parser"
                            )
                            url = video_soup.find("source")["src"]

                    elif episode["s3VideoSource"]:
                        url = f"{settings.video_cdn}{episode['s3VideoSource']['playlistPath']}"

                    elif episode["videoSource"]:
                        async with session.get(
                            episode["videoSource"]["playPath"]
                        ) as video:
                            video_soup = BeautifulSoup(
                                await video.text(), "html.parser"
                            )
                            url = video_soup.find("source")["src"]

                    # Add to streams
                    streams["streams"].append(
                        Stream(
                            name=voice_names[index]["name"],
                            url=url,
                        )
                    )

            episode_count -= settings.page_size
            page += 1

        index += 1
    return streams
