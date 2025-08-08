from enum import Enum
from hybraut_interfaces.msg import AutomatonStatus


class StatusEnum(Enum):
    INACTIVE=AutomatonStatus.INACTIVE
    ACTIVE=AutomatonStatus.ACTIVE
    TRANSITIONING=AutomatonStatus.TRANSITIONING
    WARNING=AutomatonStatus.WARNING
    ERROR=AutomatonStatus.ERROR
    RECOVERING=AutomatonStatus.RECOVERING
    FATAL=AutomatonStatus.FATAL
    MISSION_COMPLETE=AutomatonStatus.MISSION_COMPLETE