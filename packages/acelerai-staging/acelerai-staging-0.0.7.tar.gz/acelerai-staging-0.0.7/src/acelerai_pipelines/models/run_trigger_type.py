from enum import Enum


class RunTriggerType(Enum):
    Test = 0
    Cron = 1
    OnDemand = 2