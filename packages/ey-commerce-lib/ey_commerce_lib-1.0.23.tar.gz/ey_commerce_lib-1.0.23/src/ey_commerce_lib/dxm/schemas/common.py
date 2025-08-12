from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    data: list[T]
    page_size: int
    total_page: int
    total_size: int
    page_number: int
