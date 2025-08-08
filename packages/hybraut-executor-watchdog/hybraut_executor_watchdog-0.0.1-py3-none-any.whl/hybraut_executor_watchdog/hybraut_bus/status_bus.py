from dataclasses import dataclass
from rclpy.node import Node
from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup
from rclpy.qos import QoSProfile, qos_profile_system_default
from typing import Type, Callable, Any
from hybraut_interfaces.msg import AutomatonStatus
from enum import Enum

from hybraut_executor_watchdog.hybraut_consts import StatusEnum
from hybraut_executor_watchdog.hybraut_bus.ros_bus import BaseBus
from typing import Union

@dataclass
class StatusBus(BaseBus):
    """
    StatusBus implementation using the base bus functionality.
    Manages the state of the watchdog FSM.
    """
    
    def __init__(self, node: Node, status_callback: Callable,
                 topic: str = "/automaton/status",
                 msg_type: Type = AutomatonStatus,
                 qos: QoSProfile = None,
                 cb_group: CallbackGroup = None):
        
        if qos is None:
            qos = qos_profile_system_default
        if cb_group is None:
            cb_group = ReentrantCallbackGroup()
        if msg_type is None:
            msg_type = AutomatonStatus
            
        super().__init__(
            node=node,
            callback=status_callback,
            topic_name=topic,
            msg_type=msg_type,
            qos=qos,
            cb_group=cb_group
        )
    
    def _create_message(self, status: Union[Enum, Any], message: str) -> Any:
        """Create an AutomatonStatus message."""
        if AutomatonStatus:
            return AutomatonStatus(
                type=status.value if isinstance(status, Enum) else status,
                message=message,
                stamp=self.node.get_clock().now().to_msg(),
            )
        return None
    
    def publish_status(self, status: Union[Enum, Any], message: str = "") -> None:
        """Publish a status with more explicit naming."""
        self.publish(status, message)

    @classmethod
    def create_status_bus(node: Node, status_callback: Callable, **kwargs) -> 'StatusBus':
        """Factory function to create a StatusBus."""
        return StatusBus(node=node, status_callback=status_callback, **kwargs)


def main():
    """
    Main function to demonstrate the usage of EventBus.
    This is just a placeholder and should be replaced with actual usage.
    """
    import rclpy
    from rclpy.executors import MultiThreadedExecutor, Executor
    import os
    import threading

    rclpy.init()
    executor: Executor = MultiThreadedExecutor(num_threads=os.cpu_count())
    node = Node("mock_node")
    executor.add_node(node)

    thread = threading.Thread(target=executor.spin, daemon=True)
    thread.start()

    try:
        status_bus: StatusBus = StatusBus(
            node=node,
            status_callback=lambda msg: print(
                f"Received status: {msg.type}, Message: {msg.message}"
            ),
        )
        status_bus.publish(StatusEnum.ACTIVE, "hybraut is active")
        import time

        time.sleep(0.01)
        status_bus.publish(StatusEnum.TRANSITIONING, "hybraut is transitioning")
        time.sleep(0.01)

        status_bus.publish(StatusEnum.FATAL, "hybraut is in a fatal state")
        time.sleep(0.01)
    except KeyboardInterrupt:
        print("Shutting down gracefully...")
    finally:
        executor.shutdown()
        thread.join()
        node.destroy_node()

    rclpy.shutdown()

if __name__ == "__main__":
    main()
