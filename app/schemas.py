from pydantic import BaseModel
from typing import List


class Catalogs(BaseModel):
    type: str
    id: str
    name: str
    extra: list[dict]


class Manifest(BaseModel):
    id: str
    version: str
    logo: str
    name: str
    description: str
    types: list[str]
    catalogs: list[Catalogs]
    resources: list[str]
