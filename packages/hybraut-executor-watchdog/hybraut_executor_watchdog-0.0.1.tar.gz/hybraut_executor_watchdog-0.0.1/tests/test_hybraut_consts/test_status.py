import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'hybraut_executor_watchdog'))  # Adjust the path as necessary

from hybraut_executor_watchdog.constants import StatusEnum
import pytest

from hybraut_interfaces.msg import AutomatonStatus


class TestStatusEnum:
    """Test suite for StatusEnum to ensure it correctly maps to AutomatonStatus messages."""
    def test_status_enum_membership(self):
        assert hasattr(StatusEnum, 'INACTIVE')
        assert hasattr(StatusEnum, 'ACTIVE')
        assert hasattr(StatusEnum, 'TRANSITIONING')
        assert hasattr(StatusEnum, 'WARNING')
        assert hasattr(StatusEnum, 'ERROR')
        assert hasattr(StatusEnum, 'RECOVERING')
        assert hasattr(StatusEnum, 'FATAL')
        assert hasattr(StatusEnum, 'MISSION_COMPLETE')

    def test_status_enum_values(self):
        assert StatusEnum.INACTIVE.value == AutomatonStatus.INACTIVE
        assert StatusEnum.ACTIVE.value == AutomatonStatus.ACTIVE
        assert StatusEnum.TRANSITIONING.value == AutomatonStatus.TRANSITIONING
        assert StatusEnum.WARNING.value == AutomatonStatus.WARNING
        assert StatusEnum.ERROR.value == AutomatonStatus.ERROR
        assert StatusEnum.RECOVERING.value == AutomatonStatus.RECOVERING
        assert StatusEnum.FATAL.value == AutomatonStatus.FATAL
        assert StatusEnum.MISSION_COMPLETE.value == AutomatonStatus.MISSION_COMPLETE

if __name__ == "__main__":
    pytest.main([__file__])