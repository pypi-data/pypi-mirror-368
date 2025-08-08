import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'hybraut_executor_watchdog'))  # Adjust the path as necessary

from hybraut_executor_watchdog.constants import EventEnum
import pytest
from hybraut_interfaces.msg import AutomatonEvents


class TestStatusEnum:
    """Test suite for StatusEnum to ensure it correctly maps to AutomatonStatus messages."""
    def test_status_enum_membership(self):
        assert hasattr(EventEnum, 'VALID_MISSION_REQUEST')
        assert hasattr(EventEnum, 'TRANSITION_GUARD_ENABLED')
        assert hasattr(EventEnum, 'TRANSITION_COMPLETE')
        assert hasattr(EventEnum, 'RECOVERABLE_ERROR')
        assert hasattr(EventEnum, 'ATTEMPT_FIX')
        assert hasattr(EventEnum, 'RECOVERED')
        assert hasattr(EventEnum, 'RECOVERY_FAILED')
        assert hasattr(EventEnum, 'CRITICAL_FAILURE')
        assert hasattr(EventEnum, 'MISSION_COMPLETE')
        assert hasattr(EventEnum, 'SHUTDOWN')

    def test_status_enum_values(self):
        assert EventEnum.VALID_MISSION_REQUEST.value == AutomatonEvents.VALID_MISSION_REQUEST
        assert EventEnum.TRANSITION_GUARD_ENABLED.value == AutomatonEvents.TRANSITION_GUARD_ENABLED
        assert EventEnum.TRANSITION_COMPLETE.value == AutomatonEvents.TRANSITION_COMPLETE
        assert EventEnum.RECOVERABLE_ERROR.value == AutomatonEvents.RECOVERABLE_ERROR
        assert EventEnum.ATTEMPT_FIX.value == AutomatonEvents.ATTEMPT_FIX
        assert EventEnum.RECOVERED.value == AutomatonEvents.RECOVERED
        assert EventEnum.RECOVERY_FAILED.value == AutomatonEvents.RECOVERY_FAILED
        assert EventEnum.CRITICAL_FAILURE.value == AutomatonEvents.CRITICAL_FAILURE
        assert EventEnum.MISSION_COMPLETE.value == AutomatonEvents.MISSION_COMPLETE
        assert EventEnum.SHUTDOWN.value == AutomatonEvents.SHUTDOWN



if __name__ == "__main__":
    pytest.main([__file__])