import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
import threading


def main():
    rclpy.init()
    node = Node(node_name="mock_node")
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)

    thread = threading.Thread(target=executor.spin)
    thread.start()

    import os
    import sys

    sys.path.append(os.path.dirname(__file__))
    from src.hybraut_executor_watchdog.fsm import HybrautWatchdogFSM
    from hybraut_interfaces.msg import AutomatonEvents

    watchdog_instance: HybrautWatchdogFSM = HybrautWatchdogFSM(node=node)
    watchdog_instance.trigger_transition(
        AutomatonEvents(type=AutomatonEvents.TRANSITION_GUARD_ENABLED)
    )

    import time

    time.sleep(0.1)

    print(watchdog_instance.state)

    rclpy.shutdown()


if __name__ == "__main__":
    main()
