#!/usr/bin/python3
# -*- coding: utf-8  -*-
"""
Enhanced Hybraut Watchdog Finite State Machine (FSM)
This module implements a finite state machine (FSM) for the Hybraut system,
which acts as a watchdog to monitor and manage the system's operational states.
It uses the `transitions` library to define states and transitions, and integrates
with ROS 2 for status publishing and event handling.
It includes error handling and recovery mechanisms to ensure the system can
recover from various operational anomalies.

ENHANCEMENT: Transition callbacks are now optionally overridable by subclasses
to allow for custom functionality while maintaining the base behavior.
"""

# Third-party imports
from transitions import Machine
from typing import Any, Optional, Callable

# ROS 2 imports
import rclpy
from rclpy.node import Node
from rclpy.publisher import Publisher
from rclpy.impl.rcutils_logger import RcutilsLogger
from rclpy.qos import QoSProfile, qos_profile_system_default
from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup
from builtin_interfaces.msg import Time

# Message imports
from hybraut_interfaces.msg import AutomatonEvents, AutomatonStatus

# Local imports
from hybraut_executor_watchdog.hybraut_consts import StatusEnum, EventEnum
from hybraut_executor_watchdog.hybraut_bus import StatusBus, EventBus

QOS = QoSProfile(depth=10, reliability=qos_profile_system_default.reliability)


class FSM:
    """
    Finite State Machine for Hybraut watchdog.
    Separates trigger names from callbacks to avoid name collisions.
    
    Enhanced to support overridable transition callbacks:
    - Base callbacks provide default functionality
    - Subclasses can override specific callbacks to add custom behavior
    - Override hooks allow extending functionality without replacing base behavior
    """

    # Define all states
    states = [status for status in StatusEnum]

    # Map incoming EventEnum to trigger method names
    transition_function_map = {
        EventEnum.VALID_MISSION_REQUEST: "activate_mission",
        EventEnum.TRANSITION_GUARD_ENABLED: "enable_guard",
        EventEnum.TRANSITION_COMPLETE: "complete_transition",
        EventEnum.RECOVERABLE_ERROR: "handle_recoverable_error",
        EventEnum.ATTEMPT_FIX: "attempt_fix_process",
        EventEnum.RECOVERED: "complete_recovery",
        EventEnum.RECOVERY_FAILED: "fail_recovery",
        EventEnum.CRITICAL_FAILURE: "handle_critical_failure",
        EventEnum.MISSION_COMPLETE: "finish_mission",
        EventEnum.SHUTDOWN: "shutdown_system",
    }

    def __init__(
        self,
        node: Node,
        cb_group: CallbackGroup = None,
        qos: QoSProfile = None,
        initial_state: StatusEnum = StatusEnum.ACTIVE,
    ):
        if cb_group is None:
            cb_group = ReentrantCallbackGroup()
        if qos is None:
            qos = qos_profile_system_default

        # Initialize state machine, after hook will publish status
        self.machine = Machine(
            model=self,
            states=self.states,
            initial=initial_state,
            after_state_change=lambda event: self.publish_status(event),
            ignore_invalid_triggers=True,
        )
        self._add_transitions()
        self.__post_init__(node=node, cb_group=cb_group, qos=qos)

    def _add_transitions(self):
        """Add all state transitions with their callback handlers."""
        # Normal operational flow
        self.machine.add_transition(
            trigger="enable_guard",
            source=StatusEnum.ACTIVE,
            dest=StatusEnum.TRANSITIONING,
            after=self._safe_callback_wrapper("on_guard_enabled")
        )
        self.machine.add_transition(
            trigger="complete_transition",
            source=StatusEnum.TRANSITIONING,
            dest=StatusEnum.ACTIVE,
            after=self._safe_callback_wrapper("on_transition_complete")
        )
        self.machine.add_transition(
            trigger="finish_mission",
            source=StatusEnum.ACTIVE,
            dest=StatusEnum.MISSION_COMPLETE,
            after=self._safe_callback_wrapper("on_mission_complete")
        )

        # Error handling
        self.machine.add_transition(
            trigger="handle_recoverable_error",
            source=[StatusEnum.ACTIVE, StatusEnum.TRANSITIONING],
            dest=StatusEnum.ERROR,
            after=self._safe_callback_wrapper("on_recoverable_error")
        )
        self.machine.add_transition(
            trigger="attempt_fix_process",
            source=StatusEnum.ERROR,
            dest=StatusEnum.RECOVERING,
            after=self._safe_callback_wrapper("on_attempt_fix")
        )
        self.machine.add_transition(
            trigger="complete_recovery",
            source=StatusEnum.RECOVERING,
            dest=StatusEnum.ACTIVE,
            after=self._safe_callback_wrapper("on_recovered")
        )
        self.machine.add_transition(
            trigger="fail_recovery",
            source=StatusEnum.RECOVERING,
            dest=StatusEnum.ERROR,
            after=self._safe_callback_wrapper("on_recovery_failed")
        )
        self.machine.add_transition(
            trigger="handle_critical_failure",
            source=[StatusEnum.ERROR, StatusEnum.RECOVERING],
            dest=StatusEnum.FATAL,
            after=self._safe_callback_wrapper("on_critical_failure")
        )

        # Shutdown from any non-fatal state
        for state in StatusEnum:
            if state != StatusEnum.FATAL:
                self.machine.add_transition(
                    trigger="shutdown_system",
                    source=state,
                    dest=StatusEnum.FATAL,
                    after=self._safe_callback_wrapper("on_shutdown")
                )

    def _safe_callback_wrapper(self, callback_name: str) -> Callable:
        """
        Creates a safe wrapper for callback functions that handles exceptions
        and ensures the callback exists before calling it.
        
        Args:
            callback_name: Name of the callback method to wrap
            
        Returns:
            Wrapped callback function
        """
        def wrapper(event):
            try:
                callback_method = getattr(self, callback_name, None)
                if callback_method and callable(callback_method):
                    callback_method(event)
                else:
                    self.node.get_logger().warning(
                        f"Callback {callback_name} not found or not callable"
                    )
            except Exception as e:
                self.node.get_logger().error(
                    f"Error in callback {callback_name}: {e}"
                )
        return wrapper

    def __post_init__(
        self,
        node: Node,
        cb_group: CallbackGroup = None,
        qos: QoSProfile = None
    ):
        if cb_group is None:
            cb_group = ReentrantCallbackGroup()
        if qos is None:
            qos = qos_profile_system_default

        self.node = node
        self.cb_group = cb_group
        self.qos = qos

        self.status_bus: StatusBus = StatusBus(
            node=self.node,
            status_callback=self.status_callback,
            cb_group=self.cb_group,
            qos=self.qos
        )
        self.event_bus: EventBus = EventBus(
            node=node,
            event_callback=self.trigger_transition,
            cb_group=cb_group,
            qos=qos,
        )

    def status_callback(self, msg: any) -> None:
        """Handle incoming status messages. Can be overridden by subclasses."""
        self.node.get_logger().info(f"Status received: {msg}")

    def publish_status(self, event: any):
        """Publish status updates. Can be overridden by subclasses."""
        try:
            self.status_bus.publish(
                data=self.get_current_state(),
                message=f"State changed to {self.get_current_state()}",
            )
            self.node.get_logger().info(f"Published status: {self.get_current_state()}")
        except Exception as e:
            self.node.get_logger().error(f"Failed to publish status: {e}")

    def trigger_transition(self, event: AutomatonEvents):
        """Process incoming events and trigger appropriate transitions."""
        if not isinstance(event, AutomatonEvents):
            self.node.get_logger().error(f"Invalid event type: {type(event)}")
            return
        enum_dict = {enum.value: enum for enum in EventEnum}
        if event.type not in enum_dict:
            self.node.get_logger().warn(f"Unknown event: {event.type}")
            return
        event_enum = enum_dict[event.type]
        self.node.get_logger().info(f"Processing event: {event_enum}")
        self.perform_event_driven_transition(event_enum)

    def perform_event_driven_transition(self, event: EventEnum):
        """Execute the appropriate transition for the given event."""
        trigger = self.transition_function_map.get(event)
        if not trigger:
            raise ValueError(f"No trigger mapped for event {event}")
        if not hasattr(self, trigger):
            raise AttributeError(f"Trigger method {trigger} not found")
        getattr(self, trigger)(event)
        self.node.get_logger().info(f"Fired trigger: {trigger}")

    # =============================================================================
    # OVERRIDABLE TRANSITION CALLBACK HANDLERS
    # These methods can be overridden by subclasses to provide custom behavior
    # =============================================================================

    def on_guard_enabled(self, event):
        """
        Called when guard is enabled and transitioning to TRANSITIONING state.
        Override this method to add custom behavior.
        
        Args:
            event: Transition event object
        """
        self.node.get_logger().info(f"Guard enabled, transitioning: {event}")
        # Call pre/post hooks if implemented
        self._call_hook("pre_guard_enabled", event)
        self._execute_guard_enabled_logic(event)
        self._call_hook("post_guard_enabled", event)

    def on_transition_complete(self, event):
        """
        Called when transition is complete and returning to ACTIVE state.
        Override this method to add custom behavior.
        
        Args:
            event: Transition event object
        """
        self.node.get_logger().info(f"Transition complete: {event}")
        self._call_hook("pre_transition_complete", event)
        self._execute_transition_complete_logic(event)
        self._call_hook("post_transition_complete", event)

    def on_mission_complete(self, event):
        """
        Called when mission is completed.
        Override this method to add custom behavior.
        
        Args:
            event: Transition event object
        """
        self.node.get_logger().info("Mission completed successfully")
        self._call_hook("pre_mission_complete", event)
        self._execute_mission_complete_logic(event)
        self._call_hook("post_mission_complete", event)

    def on_recoverable_error(self, event):
        """
        Called when entering ERROR state due to recoverable error.
        Override this method to add custom behavior.
        
        Args:
            event: Transition event object
        """
        self.node.get_logger().warning("Entered ERROR state")
        self._call_hook("pre_recoverable_error", event)
        self._execute_recoverable_error_logic(event)
        self._call_hook("post_recoverable_error", event)

    def on_attempt_fix(self, event):
        """
        Called when attempting to recover from error.
        Override this method to add custom behavior.
        
        Args:
            event: Transition event object
        """
        self.node.get_logger().info("Attempting to recover from error")
        self._call_hook("pre_attempt_fix", event)
        self._execute_attempt_fix_logic(event)
        self._call_hook("post_attempt_fix", event)

    def on_recovered(self, event):
        """
        Called when recovery is successful.
        Override this method to add custom behavior.
        
        Args:
            event: Transition event object
        """
        self.node.get_logger().info("Recovery successful, back to ACTIVE")
        self._call_hook("pre_recovered", event)
        self._execute_recovered_logic(event)
        self._call_hook("post_recovered", event)

    def on_recovery_failed(self, event):
        """
        Called when recovery attempt fails.
        Override this method to add custom behavior.
        
        Args:
            event: Transition event object
        """
        self.node.get_logger().error("Recovery attempt failed, back in ERROR")
        self._call_hook("pre_recovery_failed", event)
        self._execute_recovery_failed_logic(event)
        self._call_hook("post_recovery_failed", event)

    def on_critical_failure(self, event):
        """
        Called when critical failure occurs.
        Override this method to add custom behavior.
        
        Args:
            event: Transition event object
        """
        self.node.get_logger().fatal("Critical failure: entering FATAL state")
        self._call_hook("pre_critical_failure", event)
        self._execute_critical_failure_logic(event)
        self._call_hook("post_critical_failure", event)

    def on_shutdown(self, event):
        """
        Called when shutdown is initiated.
        Override this method to add custom behavior.
        
        Args:
            event: Transition event object
        """
        self.node.get_logger().info("Shutdown initiated: entering FATAL state")
        self._call_hook("pre_shutdown", event)
        self._execute_shutdown_logic(event)
        self._call_hook("post_shutdown", event)

    # =============================================================================
    # HOOK SYSTEM FOR EXTENDING FUNCTIONALITY
    # These methods provide extension points without requiring full override
    # =============================================================================

    def _call_hook(self, hook_name: str, event):
        """
        Call a hook method if it exists. Hooks allow extending functionality
        without overriding the entire callback.
        
        Args:
            hook_name: Name of the hook method to call
            event: Event object to pass to the hook
        """
        hook_method = getattr(self, hook_name, None)
        if hook_method and callable(hook_method):
            try:
                hook_method(event)
            except Exception as e:
                self.node.get_logger().error(f"Error in hook {hook_name}: {e}")

    # =============================================================================
    # BASE IMPLEMENTATION METHODS
    # These contain the core logic and can be called by overridden methods
    # =============================================================================

    def _execute_guard_enabled_logic(self, event):
        """Base logic for guard enabled transition."""
        pass  # Override in subclass if needed

    def _execute_transition_complete_logic(self, event):
        """Base logic for transition complete."""
        pass  # Override in subclass if needed

    def _execute_mission_complete_logic(self, event):
        """Base logic for mission complete."""
        pass  # Override in subclass if needed

    def _execute_recoverable_error_logic(self, event):
        """Base logic for recoverable error handling."""
        pass  # Override in subclass if needed

    def _execute_attempt_fix_logic(self, event):
        """Base logic for attempt fix."""
        pass  # Override in subclass if needed

    def _execute_recovered_logic(self, event):
        """Base logic for recovery successful."""
        pass  # Override in subclass if needed

    def _execute_recovery_failed_logic(self, event):
        """Base logic for recovery failed."""
        pass  # Override in subclass if needed

    def _execute_critical_failure_logic(self, event):
        """Base logic for critical failure."""
        pass  # Override in subclass if needed

    def _execute_shutdown_logic(self, event):
        """Base logic for shutdown."""
        pass  # Override in subclass if needed

    # =============================================================================
    # UTILITY METHODS
    # =============================================================================

    def get_current_state(self) -> StatusEnum:
        """Get the current state of the FSM."""
        return self.state

    def get_valid_transitions(self) -> list:
        """Get list of valid transitions from current state."""
        return self.machine.get_triggers(self.state)

    def is_terminal_state(self) -> bool:
        """Check if current state is terminal (FATAL)."""
        return self.state == StatusEnum.FATAL

# =============================================================================
# EXAMPLE SUBCLASS DEMONSTRATING OVERRIDABLE FUNCTIONALITY
# =============================================================================

class CustomFSM(FSM):
    """
    Example subclass demonstrating how to override transition callbacks
    to add custom functionality while maintaining base behavior.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_count = 0
        self.recovery_attempts = 0

    def on_recoverable_error(self, event):
        """Override to add error tracking."""
        # Call parent implementation first
        super().on_recoverable_error(event)
        
        # Add custom behavior
        self.error_count += 1
        self.node.get_logger().info(f"Total errors encountered: {self.error_count}")
        
        # Perform additional error analysis
        if self.error_count > 5:
            self.node.get_logger().warning("High error count detected!")

    def on_attempt_fix(self, event):
        """Override to add recovery attempt tracking."""
        # Call parent implementation
        super().on_attempt_fix(event)
        
        # Add custom behavior
        self.recovery_attempts += 1
        self.node.get_logger().info(f"Recovery attempt #{self.recovery_attempts}")

    def pre_guard_enabled(self, event):
        """Hook called before guard enabled logic."""
        self.node.get_logger().info("Preparing for guard activation...")

    def post_mission_complete(self, event):
        """Hook called after mission complete logic."""
        self.node.get_logger().info(f"Mission statistics: {self.error_count} errors, {self.recovery_attempts} recoveries")

    def _execute_shutdown_logic(self, event):
        """Custom shutdown logic."""
        self.node.get_logger().info("Performing custom cleanup before shutdown...")
        # Add custom cleanup code here


def main():
    """
    Main function to demonstrate the usage of both base and custom FSM.
    """
    import os
    import threading
    import time
    from rclpy.executors import MultiThreadedExecutor, Executor
    from rclpy.callback_groups import ReentrantCallbackGroup
    
    rclpy.init()
    
    try:
        executor: Executor = MultiThreadedExecutor(num_threads=os.cpu_count())
        node = Node("hybraut_watchdog_demo")
        executor.add_node(node)
        
        # Start executor in background thread
        thread = threading.Thread(target=executor.spin, daemon=True)
        thread.start()
        
        # Create Custom FSM instance (instead of base FSM)
        fsm = CustomFSM(node=node, cb_group=ReentrantCallbackGroup(), qos=QOS)
        
        # Create event publisher for testing
        event_publisher = node.create_publisher(
            AutomatonEvents, "/automaton/events", 
            qos_profile=QOS, callback_group=ReentrantCallbackGroup()
        )
        
        # Wait for connections
        time.sleep(1.0)
        
        # Test sequence including error scenarios
        test_events = [
            (EventEnum.TRANSITION_GUARD_ENABLED, "mode guard activated"),
            (EventEnum.TRANSITION_COMPLETE, "transition completed"),
            (EventEnum.RECOVERABLE_ERROR, "recoverable error occurred"),
            (EventEnum.ATTEMPT_FIX, "attempting recovery"),
            (EventEnum.RECOVERED, "system recovered"),
            (EventEnum.TRANSITION_GUARD_ENABLED, "mode guard activated"),
            (EventEnum.TRANSITION_COMPLETE, "transition completed"),
            (EventEnum.MISSION_COMPLETE, "mission has completed"),
        ]
        
        print(f"Starting Custom FSM demo. Initial state: {fsm.get_current_state()}")
        
        for event_type, message in test_events:
            print(f"\nPublishing event: {event_type.name}")
            event_msg = AutomatonEvents(type=event_type.value, message=message)
            event_publisher.publish(event_msg)
            time.sleep(0.5)
            print(f"Current state: {fsm.get_current_state()}")
            print(f"Valid transitions: {fsm.get_valid_transitions()}")
        
        print(f"\nFinal state: {fsm.get_current_state()}")
        print(f"Is terminal state: {fsm.is_terminal_state()}")
        
        time.sleep(1.0)  # Give time for final message processing
        
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'executor' in locals():
            executor.shutdown()
        if 'thread' in locals():
            thread.join()
        if 'node' in locals():
            node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()