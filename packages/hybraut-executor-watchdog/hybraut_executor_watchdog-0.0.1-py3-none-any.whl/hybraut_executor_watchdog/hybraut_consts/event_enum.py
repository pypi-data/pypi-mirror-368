from enum import Enum
from hybraut_interfaces.msg import AutomatonEvents


class EventEnum(Enum):
    VALID_MISSION_REQUEST = AutomatonEvents.VALID_MISSION_REQUEST
    TRANSITION_GUARD_ENABLED = AutomatonEvents.TRANSITION_GUARD_ENABLED
    TRANSITION_COMPLETE = AutomatonEvents.TRANSITION_COMPLETE
    RECOVERABLE_ERROR = AutomatonEvents.RECOVERABLE_ERROR
    ATTEMPT_FIX = AutomatonEvents.ATTEMPT_FIX
    RECOVERED = AutomatonEvents.RECOVERED
    RECOVERY_FAILED = AutomatonEvents.RECOVERY_FAILED
    CRITICAL_FAILURE = AutomatonEvents.CRITICAL_FAILURE
    MISSION_COMPLETE = AutomatonEvents.MISSION_COMPLETE
    SHUTDOWN = AutomatonEvents.SHUTDOWN
