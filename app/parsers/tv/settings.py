from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    name: str = "TVUA"


settings = Settings()
