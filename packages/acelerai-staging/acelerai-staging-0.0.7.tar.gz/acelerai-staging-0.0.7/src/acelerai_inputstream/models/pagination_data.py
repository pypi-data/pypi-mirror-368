from typing import TypeVar, Generic, Optional
T = TypeVar('T')

class PaginationData(Generic[T]):
    """
    A class to represent paginated data.

    Attributes:
        total_items (int): Total number of items across all pages.
        total_pages (int): Total number of pages.
        page (int): Current page number.
        page_size (int): Number of items per page.
        data (list[T]): List of items in the current page.
    """

    total_items: int
    total_pages: int
    page: int
    page_size: int
    data: list[T]

    def __init__(self, data: list[T], total_items:int, page:int, page_size:int):
        """
        Initializes the PaginationData with items, total count, current page, and page size.
        :param items: List of items in the current page.
        :param total: Total number of items across all pages.
        :param page: Current page number.
        :param page_size: Number of items per page.
        """
        self.data = data
        self.total_items = total_items
        self.total_pages = (total_items + page_size - 1) // page_size
        self.page = page
        self.page_size = page_size

    def __repr__(self):
        return f"total_pages={self.total_pages}, total_items={self.total_items}, page={self.page}, page_size={self.page_size}, len_page={len(self.data)}"
    
    def __len__(self):
        """
        Returns the number of items in the current page.
        """
        return len(self.data)