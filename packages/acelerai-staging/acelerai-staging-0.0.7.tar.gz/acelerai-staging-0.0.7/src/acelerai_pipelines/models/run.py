from copy import deepcopy
from enum import Enum
from uuid import UUID
from datetime import datetime
from acelerai_pipelines.util import toUpperFirst
from .run_trigger_type import RunTriggerType
from .environment_item import EnvironmentItem


class RunStatus(Enum):
    Pending = 0
    Running = 1
    Error = 2
    Completed = 3
    Cancelled = 4
    InternalError = 5
    Lost = 6


class StepStatus(Enum):
    Waiting = 0
    Building = 1
    Running = 2
    Error = 3
    Success = 4


class RunParams:
    NodesIds: list[UUID]
    ProjectId: UUID
    ProjectName: str
    RunImageId: UUID
    GitServerId: UUID
    ProjectGitId: UUID
    LastCommitSelected: bool
    ForceWriteLogs: bool
    CommitHash: str
    CommitComment: str
    Environments: list[EnvironmentItem]
    Notebooks: list[str]
    Timeouts: list[int]
    Payload: str

    def __init__(self, **kwargs):
        kwargs = {k.capitalize(): v for k, v in kwargs.items()}
        kwargs["Environments"] = [EnvironmentItem(**env) for env in kwargs["Environments"]]
        self.__dict__ = kwargs

    def get_dict(self):
        data = deepcopy(self.__dict__)
        data["Environments"] = [env.get_dict() for env in self.Environments]
        return data


class StepControlProps:
    Name: str
    FilePath: str
    StartTime: datetime
    EndTime: datetime
    StepLogs: str
    StepStatus: StepStatus
    JupyterOut: str
    LogsSize: int
    HTMLSize: int

    def __init__(self,**kwargs):
        kwargs = {toUpperFirst(k): v for k, v in kwargs.items()}
        kwargs["StepStatus"] = StepStatus(kwargs["StepStatus"])
        self.__dict__ = kwargs

    def get_dict(self):
        data = deepcopy(self.__dict__)
        data["StepStatus"] = self.StepStatus.value
        return data


class Run:
    Id: UUID
    SubscriptionId: UUID
    DeployId: UUID
    RunTriggerType: RunTriggerType
    RunStatus: RunStatus
    CreatedOn: datetime
    EnqueuedTime: datetime
    SocketRoomName: str
    RunParams: RunParams
    StepsControlProps: list[StepControlProps]
    ImageStartTime: datetime
    ImageFinishTime: datetime
    LastPing: datetime
    Result:str
    PodName: str
    NodeName: str

    def __init__(self, **kwargs):
        # capitalize all keys
        kwargs = {toUpperFirst(k): v for k, v in kwargs.items()}

        kwargs["RunTriggerType"] = RunTriggerType(kwargs["RunTriggerType"])
        kwargs["RunStatus"] = RunStatus(kwargs["RunStatus"])
        kwargs["RunParams"] = RunParams(**kwargs["RunParams"])
        kwargs["StepsControlProps"] = [StepControlProps(**step) for step in kwargs["StepsControlProps"]] if kwargs["StepsControlProps"] else None
        self.__dict__ = kwargs

    def get_dict(self):
        data = deepcopy(self.__dict__)
        data["RunTriggerType"] = self.RunTriggerType.value
        data["RunStatus"] = self.RunStatus.value
        data["RunParams"] = self.RunParams.get_dict()
        data["StepsControlProps"] = [step.get_dict() for step in self.StepsControlProps]
        return data
