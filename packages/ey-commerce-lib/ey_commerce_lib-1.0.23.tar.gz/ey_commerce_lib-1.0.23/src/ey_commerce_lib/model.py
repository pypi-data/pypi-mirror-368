from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar('T')


class Page(Generic[T], BaseModel):
    records: list[T]
    page_number: int
    page_size: int
    total: int
    total_page: int
