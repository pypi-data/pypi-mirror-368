from typing import TypeVar, Generic

T = TypeVar('T')
class PaginationData(Generic[T]):
    """
    Pagination data class
    """
    data: list[T]
    page: int
    page_size: int
    total: int

    def __init__(self, data: list[T], page: int, page_size: int, total: int):
        self.data = data
        self.page = page
        self.page_size = page_size
        self.total = total