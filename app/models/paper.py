from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


PaperSource = Literal["arxiv", "dblp", "imported"]


class Paper(BaseModel):
    source: PaperSource
    source_id: str | None = None
    title: str
    authors: list[str] = Field(default_factory=list)
    abstract: str = ""
    venue: str | None = None
    published_date: date | None = None
    year: int | None = None
    doi: str | None = None
    url: str | None = None
    preset_tags: list[str] = Field(default_factory=list)
    free_tags: list[str] = Field(default_factory=list)
