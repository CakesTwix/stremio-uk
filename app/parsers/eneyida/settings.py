from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    name: str = "Eneyida.tv"
    main_url: str = "https://eneyida.tv"

settings = Settings()
