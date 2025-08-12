from copy import deepcopy
from uuid import UUID
from enum import Enum
from datetime import datetime

from acelerai_pipelines.util import toUpperFirst
from .run_trigger_type import RunTriggerType
from .environment_item import EnvironmentItem


class DeployType(Enum):
    OnDemand = 0
    OnDemandAndScheduled = 1


class DeployInfo:
    FKey: str
    CronExpression: str
    Actived: bool
    DeployType: DeployType

    def __init__(self, **kwargs):
        kwargs = {toUpperFirst(k): v for k, v in kwargs.items()}
        kwargs["DeployType"] = DeployType(kwargs["DeployType"])
        self.__dict__ = kwargs

    def get_dict(self):
        data = deepcopy(self.__dict__)
        data["DeployType"] = self.DeployType.value
        return data


class DeployParams:
    NodesIds: list[UUID]
    RunImageId: UUID
    GitServerId: UUID
    ProjectGitId: UUID
    ForceWriteLogs: bool
    LastCommitSelected: bool
    CommitHash: str
    CommitComment: str
    Environments: list[EnvironmentItem]
    Notebooks: list[str]
    Timeouts: list[int]
    PayloadSchema: str

    def __init__(self, **kwargs):
        kwargs = {toUpperFirst(k): v for k, v in kwargs.items()}
        kwargs["Environments"] = [EnvironmentItem(**env) for env in kwargs["Environments"]]
        self.__dict__ = kwargs

    def get_dict(self):
        data = deepcopy(self.__dict__)
        data["Environments"] = [env.get_dict() for env in self.Environments]
        return data


class CommunicationInfo:
    Inputs: list
    Outputs: list
    Communications: list

    def __init__(self,**kwargs):
        kwargs = {toUpperFirst(k): v for k, v in kwargs.items()}
        self.__dict__ = kwargs

    def get_dict(self):
        data = deepcopy(self.__dict__)
        return data


class StatusControl:
    MinutesInterval: int
    LastError: datetime
    LastOk: datetime
    OkRunId: UUID
    ErrorRunId: UUID
    OkTriggerType: RunTriggerType
    ErrorTriggerType: RunTriggerType

    def __init__(self, **kwargs):
        kwargs = {toUpperFirst(k): v for k, v in kwargs.items()}
        kwargs["OkTriggerType"] = RunTriggerType(kwargs["OkTriggerType"]) if kwargs["OkTriggerType"] else None
        kwargs["ErrorTriggerType"] = RunTriggerType(kwargs["ErrorTriggerType"]) if kwargs["ErrorTriggerType"] else None
        self.__dict__ = kwargs
    
    def get_dict(self):
        data = deepcopy(self.__dict__)
        data["OkTriggerType"] = self.OkTriggerType.value if self.OkTriggerType else None
        data["ErrorTriggerType"] = self.ErrorTriggerType.value if self.ErrorTriggerType else None
        return data


class Deploy:
    Id: UUID
    SubscriptionId: UUID
    ProjectId: UUID
    Name: str
    Description: str
    DeployInfo: DeployInfo
    DeployParams: DeployParams
    CommunicationInfo: CommunicationInfo
    StatusControl: StatusControl
    CreatedOn: datetime
    RemovedOn: datetime
    Removed: bool

    def __init__(self,**kwargs):
        # first letter of to upper case
        kwargs = {toUpperFirst(k) : v for k, v in kwargs.items()}
        kwargs["DeployInfo"] = DeployInfo(**kwargs["DeployInfo"])
        kwargs["DeployParams"] = DeployParams(**kwargs["DeployParams"])
        kwargs["CommunicationInfo"] = CommunicationInfo(**kwargs["CommunicationInfo"]) if kwargs["CommunicationInfo"] else None
        kwargs["StatusControl"] = StatusControl(**kwargs["StatusControl"])

        self.__dict__ = kwargs

    def get_dict(self):
        data = deepcopy(self.__dict__)
        data["DeployInfo"] = self.DeployInfo.get_dict()
        data["DeployParams"] = self.DeployParams.get_dict()
        data["CommunicationInfo"] = self.CommunicationInfo.get_dict() if self.CommunicationInfo else None
        data["StatusControl"] = self.StatusControl.get_dict()
        return data
