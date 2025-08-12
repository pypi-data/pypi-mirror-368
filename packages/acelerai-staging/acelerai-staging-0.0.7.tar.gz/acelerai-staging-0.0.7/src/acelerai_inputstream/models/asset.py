

class Asset:
    """
    Represents an asset in the AcelerAI.
    Attributes:
        id (str): Unique identifier for the asset.
        path (str): path of the asset.
        created_on (str): Creation date of the asset.
    """
    id: str
    path: str
    created_at: str
    url: str
    size: int

    def __init__(self, id: str, path: str, created_at: str, url: str, size:int):
        """
        Initializes the Asset with id, path, and creation date.
        :param id: Unique identifier for the asset.
        :param path: path of the asset.
        :param created_at: Creation date of the asset.
        """
        self.id = id
        self.url = url
        self.path = path
        self.size = size
        self.created_at = created_at