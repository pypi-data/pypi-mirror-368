"""
a simple script for testing the hybraut watchdog FSMp
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, qos_profile_system_default
from rclpy.executors import MultiThreadedExecutor, Executor
import threading
from hybraut_interfaces.msg import AutomatonEvents, AutomatonStatus
from rclpy.executors import MultiThreadedExecutor, SingleThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup, MutuallyExclusiveCallbackGroup
import os
from rclpy.publisher import Publisher
from rclpy.subscription import Subscription
import time

# import sys

# # sys.path.append(os.path.dirname(__file__))

# from hybraut_watchdog import HybrautWatchdogFSM
from hybraut_executor.watchdog import HybrautWatchdogFSM


def main():
    rclpy.init()

    executor: Executor = MultiThreadedExecutor(num_threads=2)

    node = Node("mock_node")

    event_publisher: Publisher = node.create_publisher(
        msg_type=AutomatonEvents,
        topic="/automaton/events",
        qos_profile=qos_profile_system_default,
        callback_group=ReentrantCallbackGroup(),
    )

    def status_callback(msg: AutomatonStatus):
        node.get_logger().info(f"status msg received: {msg}")

    status_subscription: Subscription = node.create_subscription(
        msg_type=AutomatonStatus,
        topic="/automaton/status",
        qos_profile=qos_profile_system_default,
        callback=status_callback,
        callback_group=ReentrantCallbackGroup(),
    )
    executor.add_node(node)

    thread = threading.Thread(target=executor.spin, daemon=True)
    thread.start()

    try:
        watchdogFSM: HybrautWatchdogFSM = HybrautWatchdogFSM(node)

        # Test 1. transition to TRANSITIONING STATE
        tranisition_event: AutomatonEvents = AutomatonEvents(
            type=AutomatonEvents.TRANSITION_GUARD_ENABLED
        )
        event_publisher.publish(tranisition_event)
        time.sleep(0.5)
        # print(current_status)
        # current_status = None

        # Test 2: Transition back to active state
        # tranisition_event = AutomatonEvents(type=AutomatonEvents.TRANSITION_COMPLETE)
        # event_publisher.publish(tranisition_event)
        # time.sleep(0.02)
        # current_status = None

        # # Test 3: Transition to error state
        # tranisition_event = AutomatonEvents(type=AutomatonEvents.RECOVERABLE_ERROR)
        # event_publisher.publish(tranisition_event)
        # time.sleep(0.02)
        # current_status = None

        # watchdogFSM.trigger_transition(AutomatonEvents(
        #     type=AutomatonEvents.RECOVERABLE_ERROR
        # ))
        # # Test 4: Attempt fix
        # watchdogFSM.trigger_transition(AutomatonEvents(
        #     type=AutomatonEvents.ATTEMPT_FIX
        # ))
        # # Test 5: recovered
        # watchdogFSM.trigger_transition(AutomatonEvents(
        #     type=AutomatonEvents.RECOVERED
        # ))
        # # TODO: FIX Test 6: transition and recoverable error
        # watchdogFSM.trigger_transition(AutomatonEvents(
        #     type=AutomatonEvents.TRANSITION_GUARD_ENABLED
        # ))
        # watchdogFSM.trigger_transition(AutomatonEvents(
        #     type=AutomatonEvents.RECOVERABLE_ERROR # TODO: need to fix this transition it is not being recognised
        # ))
        # Test 7: fatal

        # Test 8: Mission Complete
        watchdogFSM.trigger_transition(
            AutomatonEvents(type=AutomatonEvents.MISSION_COMPLETE)
        )
    except KeyboardInterrupt:
        print("Shutting down gracefully...")
    finally:
        executor.shutdown()
        thread.join()
        node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
