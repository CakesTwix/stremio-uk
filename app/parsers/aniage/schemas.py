from pydantic import BaseModel


class Preview(BaseModel):
    id: str
    type: str = "series"
    name: str
    genres: list[str]
    poster: str
    description: str


class Series(Preview):
    director: list[str]
    runtime: str
    background: str
