from pydantic import BaseModel
from typing import List


class Preview(BaseModel):
    id: str
    type: str
    name: str
    genres: list[str]
    poster: str
    description: str


class Videos(BaseModel):
    id: str
    title: str
    thumbnail: str
    released: str
    season: int
    episode: int


class Series(Preview):
    director: list[str]
    runtime: str
    background: str
    videos: list[Videos]


class Stream(BaseModel):
    name: str
    url: str | list[str] | None
