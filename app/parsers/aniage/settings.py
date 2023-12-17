from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    name: str = "Aniage"
    main_url: str = "https://aniage.net"
    api_url: str = "https://master.api.aniage.net"
    latest_url: str = f"{api_url}/v2/anime/find"
    image_url: str = "https://image.aniage.net"
    video_cdn: str = "https://aniage-video-stream.b-cdn.net/"
    finder_url: str = "https://finder-master.api.aniage.net/"

    page_size: int = 100


settings = Settings()
