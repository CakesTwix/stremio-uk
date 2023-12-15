from bs4 import BeautifulSoup
from .schemas import Preview, Series, Videos, Stream
import aiohttp
import json

image_url = "https://image.aniage.net"  # TODO: move this to the environment vars
api_url = "https://master.api.aniage.net"
video_cdn = "https://aniage-video-stream.b-cdn.net/"


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
                poster=f'{image_url}/main/{item["posterId"]}?optimize=image&width=296',
                description=item["description"],
            )
        )

    return previews_metadata


async def get_series_metadata(
    id: str, response_text: str, videos: list[Videos]
) -> dict[str, Series]:
    soup = BeautifulSoup(response_text, "html.parser")
    response_data = json.loads(soup.find("script", type="application/json").text)

    return {
        "meta": Series(
            id=f"aniage/{id}",
            name=response_data["props"]["pageProps"]["title"],
            poster=f'{image_url}/main/{response_data["props"]["pageProps"]["posterId"]}',
            genres=response_data["props"]["pageProps"]["genres"],
            description=response_data["props"]["pageProps"]["description"],
            director=response_data["props"]["pageProps"]["studios"],
            runtime=f'{response_data["props"]["pageProps"]["averageDuration"]} хв.',
            background=f'{image_url}/main/{response_data["props"]["pageProps"]["posterId"]}',
            videos=videos,
        )
    }


async def get_videos(
    id: str, response_text: str, session: aiohttp.ClientSession
) -> list[Videos]:
    videos = []

    soup = BeautifulSoup(response_text, "html.parser")
    response_data = json.loads(soup.find("script", type="application/json").text)

    # Getting list voices
    voice = response_data["props"]["pageProps"]["teams"][0]
    # String build for get voice names
    string_team = f"{api_url}/anime/teams/by-ids?"
    string_team += f"ids={voice['teamId']}&"

    async with session.get(string_team) as response:
        voice_names = await response.json()

    index = 0
    for voice in voice_names:
        # Do list of episodes
        async with session.get(
            f"{api_url}/anime/episodes?animeId={id}&page=1&pageSize=30&sortOrder=ASC&teamId={voice['id']}&volume=1"
        ) as episodes:
            for episode in await episodes.json():
                episode_name = (
                    f"Серія {episode['episodeNum']}"
                    if episode["title"] in [". ", "."]
                    or episode["title"] == episode["episodeNum"]
                    else f"Серія {episode['episodeNum']} - {episode['title']}"
                )

                if episode["videoSource"]:
                    thumbnail = f"{image_url}/main/{episode['videoSource']['previewPath']}"
                elif episode["playPath"]:
                    thumbnail = (
                        f"{image_url}/main/{episode['previewPath']}"
                    )
                elif episode["s3VideoSource"]:
                    thumbnail = f"{image_url}/{episode['s3VideoSource']['previewPath']}"

                videos.append(
                    Videos(
                        id=f'aniage/{episode["animeId"]}/{episode["episodeNum"]}',
                        title=episode_name,
                        thumbnail=thumbnail,
                        released=episode["lastUpdated"],
                        season=episode["volume"],
                        episode=episode["episodeNum"],
                    )
                )

        index += 1

    return videos


async def get_streams(
    id: str, episodeNum: int, session: aiohttp.ClientSession, response_data
) -> dict[str, list[Stream]]:
    streams = {"streams": []}

    soup = BeautifulSoup(response_data, "html.parser")
    response_data = json.loads(soup.find("script", type="application/json").text)

    string_team = f"{api_url}/anime/teams/by-ids?"
    # Getting list voices
    for voice in response_data["props"]["pageProps"]["teams"]:
        # String build for get voice names
        string_team += f"ids={voice['teamId']}&"

    async with session.get(string_team) as response:
        voice_names = await response.json()

    index = 0
    for voice in voice_names:
        # Do list of episodes
        async with session.get(
            f"{api_url}/anime/episodes?animeId={id}&page=1&pageSize=30&sortOrder=ASC&teamId={voice['id']}&volume=1"
        ) as episodes:
            for episode in await episodes.json():
                if int(episode["episodeNum"]) != episodeNum:
                    continue

                url = None
                if episode["playPath"]:
                    async with session.get(episode["playPath"]) as video:
                        video_soup = BeautifulSoup(
                            await video.text(), "html.parser"
                        )
                        url = video_soup.find("source")["src"]

                elif episode["s3VideoSource"]:
                    url = f"{video_cdn}{episode['s3VideoSource']['playlistPath']}"

                elif episode["videoSource"]:
                    async with session.get(
                        episode["videoSource"]["playPath"]
                    ) as video:
                        video_soup = BeautifulSoup(
                            await video.text(), "html.parser"
                        )
                        url = video_soup.find("source")["src"]

                streams["streams"].append(
                    Stream(
                        name=voice_names[index]["name"],
                        url=url,
                    )
                )

        index += 1
    return streams
