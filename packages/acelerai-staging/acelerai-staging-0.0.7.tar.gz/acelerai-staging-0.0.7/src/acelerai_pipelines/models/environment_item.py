from copy import deepcopy

from acelerai_pipelines.util import toUpperFirst

class EnvironmentItem:
    Name: str
    Value: str

    def __init__(self, **kwargs):
        kwargs = {toUpperFirst(k): v for k, v in kwargs.items()}
        self.__dict__ = kwargs

    def get_dict(self):
        data = deepcopy(self.__dict__)
        return data