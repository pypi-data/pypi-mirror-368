from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Type, Union, Any
from rclpy.node import Node
from rclpy.subscription import Subscription
from rclpy.publisher import Publisher
from rclpy.qos import QoSProfile, qos_profile_system_default
from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup
from enum import Enum

# Import your message types and enums
try:
    from hybraut_interfaces.msg import AutomatonEvents, AutomatonStatus
    from ..hybraut_consts import EventEnum, StatusEnum
except ImportError:
    # Fallback for when imports aren't available
    AutomatonEvents = None
    AutomatonStatus = None
    EventEnum = None
    StatusEnum = None


class ROSBusInterface(ABC):
    """
    Abstract interface for ROS2 bus implementations.
    Defines the contract that all bus classes should follow.
    """
    
    @abstractmethod
    def publish(self, data: Union[Enum, Any], message: str = "") -> None:
        """Publish data to the bus."""
        pass
    
    @abstractmethod
    def destroy(self) -> None:
        """Clean up resources."""
        pass
    
    @property
    @abstractmethod
    def topic(self) -> str:
        """Get the topic name."""
        pass
    
    @property
    @abstractmethod
    def is_active(self) -> bool:
        """Check if the bus is active."""
        pass

@dataclass
class BaseBus(ROSBusInterface):
    """
    Base implementation for ROS2 buses with common functionality.
    This class handles the common patterns shared between EventBus and StatusBus.
    """
    
    node: Node = field(init=True)
    callback: Callable = field(init=True)
    topic_name: str = field(init=True)
    msg_type: Type = field(init=True)
    qos: QoSProfile = field(default_factory=qos_profile_system_default, init=True)
    cb_group: CallbackGroup = field(default_factory=lambda: ReentrantCallbackGroup(), init=True)
    
    # Internal fields
    subscription: Subscription = field(default=None, init=False)
    publisher: Publisher = field(default=None, init=False)
    _active: bool = field(default=False, init=False)
    
    def __post_init__(self):
        """Initialize the ROS2 publisher and subscriber."""
        try:
            self.publisher = self.node.create_publisher(
                self.msg_type, self.topic_name, self.qos, callback_group=self.cb_group
            )
            self.subscription = self.node.create_subscription(
                self.msg_type,
                self.topic_name,
                lambda msg: self.callback(msg),
                self.qos,
                callback_group=self.cb_group,
            )
            self._active = True
        except Exception as e:
            print(f"Failed to initialize bus: {e}")
            self._active = False
    
    @property
    def topic(self) -> str:
        """Get the topic name."""
        return self.topic_name
    
    @property
    def is_active(self) -> bool:
        """Check if the bus is active."""
        return self._active and self.publisher is not None and self.subscription is not None
    
    def _create_message(self, data: Union[Enum, Any], message: str) -> Any:
        """Create a message instance. Should be overridden by subclasses."""
        # This is a generic implementation - subclasses should override
        if hasattr(self.msg_type, '__call__'):
            try:
                return self.msg_type(
                    type=data.value if isinstance(data, Enum) else data,
                    message=message,
                    stamp=self.node.get_clock().now().to_msg(),
                )
            except Exception:
                # Fallback for different message structures
                return self.msg_type()
        return None
    
    def publish(self, data: Union[Enum, Any], message: str = "") -> None:
        """Publish data to the bus."""
        if not self.is_active:
            print(f"Bus on topic '{self.topic_name}' is not active")
            return
        
        try:
            msg = self._create_message(data, message)
            if msg:
                self.publisher.publish(msg)
        except Exception as e:
            print(f"Failed to publish message: {e}")
    
    def destroy(self) -> None:
        """Clean up resources."""
        if self.subscription:
            self.node.destroy_subscription(self.subscription)
            self.subscription = None
        
        if self.publisher:
            self.node.destroy_publisher(self.publisher)
            self.publisher = None
        
        self._active = False
        self.node = None