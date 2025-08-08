import pytest
from hybraut_executor_watchdog.comm import EventBus

@pytest.fixture
def mock_components():
    """
    Mock components for testing EventBus.
    """
    import rclpy
    from rclpy.node import Node
    from rclpy.executors import MultiThreadedExecutor
    import threading
    from hybraut_interfaces.msg import AutomatonEvents
    from rclpy.qos import QoSProfile, qos_profile_system_default
    from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup

    node: Node = Node("mock_node")
    executor: MultiThreadedExecutor = MultiThreadedExecutor(num_threads=1)
    executor.add_node(node)
    
    event_callback = lambda msg: print(f"Received event: {msg.type}, message: {msg.message}")
    msg_type = AutomatonEvents
    topic = "/automaton/events"
    qos = qos_profile_system_default()
    cb_group = ReentrantCallbackGroup()

    executor_thread =threading.Thread(target=executor.spin, daemon=True)
    executor_thread.start()

    yield node, event_callback, msg_type, topic, qos, cb_group


class TestEventBus: 
    def test_event_bus_initialization(self):
        pass


if __name__ == "__main__":
    pytest.main([__file__])
