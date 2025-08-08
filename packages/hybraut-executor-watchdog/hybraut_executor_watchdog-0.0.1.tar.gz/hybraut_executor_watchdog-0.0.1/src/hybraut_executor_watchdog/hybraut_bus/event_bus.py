from hybraut_interfaces.msg import AutomatonEvents
from dataclasses import dataclass
from typing import Callable

from rclpy.node import Node
from rclpy.qos import QoSProfile, qos_profile_system_default
from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup

from hybraut_executor_watchdog.hybraut_bus.ros_bus import BaseBus
from hybraut_executor_watchdog.hybraut_consts import EventEnum
from typing import Type, Union, Any
from enum import Enum


@dataclass
class EventBus(BaseBus):
    """
    EventBus implementation using the base bus functionality.
    Manages events for the watchdog FSM.
    """
    
    def __init__(self, node: Node, event_callback: Callable, 
                 topic: str = "/automaton/events", 
                 msg_type: Type = AutomatonEvents,
                 qos: QoSProfile = None,
                 cb_group: CallbackGroup = None):
        
        if qos is None:
            qos = qos_profile_system_default
        if cb_group is None:
            cb_group = ReentrantCallbackGroup()
        if msg_type is None:
            msg_type = AutomatonEvents
            
        super().__init__(
            node=node,
            callback=event_callback,
            topic_name=topic,
            msg_type=msg_type,
            qos=qos,
            cb_group=cb_group
        )
    
    def _create_message(self, event: Union[Enum, Any], message: str) -> Any:
        """Create an AutomatonEvents message."""
        if AutomatonEvents:
            return AutomatonEvents(
                type=event.value if isinstance(event, Enum) else event,
                message=message,
                stamp=self.node.get_clock().now().to_msg(),
            )
        return None
    
    def publish_event(self, event: Union[Enum, Any], message: str = "") -> None:
        """Publish an event with more explicit naming."""
        self.publish(event, message)

    @classmethod
    def create_event_bus(node: Node, event_callback: Callable, **kwargs) -> 'EventBus':
        """Factory function to create an EventBus."""
        return EventBus(node=node, event_callback=event_callback, **kwargs)


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
        event_bus: EventBus = EventBus(
            node=node,
            event_callback=lambda msg: print(
                f"Received event: {msg.type}, Message: {msg.message}"
            ),
        )
        event_bus.publish(EventEnum.TRANSITION_GUARD_ENABLED, "mode guard activated")
        import time

        time.sleep(0.01)
        event_bus.publish(EventEnum.TRANSITION_COMPLETE, "transition completed")
        time.sleep(0.01)

        event_bus.publish(EventEnum.RECOVERY_FAILED, "mode guard deactivated")
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
