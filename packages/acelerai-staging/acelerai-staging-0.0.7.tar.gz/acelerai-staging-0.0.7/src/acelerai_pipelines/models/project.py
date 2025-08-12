from datetime import datetime
from enum import Enum
from uuid import UUID
from acelerai_pipelines.util import toUpperFirst


class Project:
    Id: UUID
    SubscriptionId : UUID
    GitServerId: UUID | None
    ProjectGitId: UUID
    StorageCredentialId: UUID
    Name: str
    Description: str
    Tags: list[str]
    Removed: bool
    CreatedOn: datetime
    RemovedOn: datetime | None

    def __init__(self, **kwargs):
        kwargs = {toUpperFirst(k): v for k, v in kwargs.items()}
        self.__dict__ = kwargs