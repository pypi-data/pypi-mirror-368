"""Event system for cross-component communication in TestAPIX.

This module provides a lightweight, type-safe event system that enables
decoupled communication between different components of the TestAPIX
framework. Components can emit events and subscribe to events without
direct dependencies on each other.
"""

from __future__ import annotations

import asyncio
import logging
import threading
import uuid
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, TypeVar

from testapix.core.exceptions import TestAPIXError

logger = logging.getLogger(__name__)

T = TypeVar("T")
EventHandler = Callable[[Any], None] | Callable[[Any], Awaitable[None]]


class EventError(TestAPIXError):
    """Raised when event operations fail."""

    def __init__(self, message: str, event_type: str | None = None) -> None:
        super().__init__(message)
        self.event_type = event_type


class EventPriority(Enum):
    """Priority levels for event handling."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class TestAPIXEvent:
    """Base event class for all TestAPIX events.

    Events are immutable data structures that carry information about
    something that happened in the system. They include metadata for
    tracking, debugging, and auditing purposes.
    """

    event_type: str
    data: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source: str | None = None
    priority: EventPriority = EventPriority.NORMAL
    correlation_id: str | None = None

    def __post_init__(self) -> None:
        """Validate event after initialization."""
        if not self.event_type:
            raise ValueError("Event type cannot be empty")

    def __str__(self) -> str:
        """Return string representation of the event."""
        return f"{self.event_type}({self.event_id})"

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "event_id": self.event_id,
            "source": self.source,
            "priority": self.priority.name,
            "correlation_id": self.correlation_id,
        }


class EventFilter(ABC):
    """Abstract base class for event filters.

    Filters allow selective event handling based on event properties
    or data content. This enables more granular control over which
    events trigger specific handlers.
    """

    @abstractmethod
    def matches(self, event: TestAPIXEvent) -> bool:
        """Check if the event matches this filter.

        Args:
        ----
            event: Event to check

        Returns:
        -------
            True if event matches filter criteria, False otherwise

        """


class TypeFilter(EventFilter):
    """Filter events by event type pattern."""

    def __init__(self, pattern: str, exact_match: bool = True) -> None:
        """Initialize type filter.

        Args:
        ----
            pattern: Event type pattern to match
            exact_match: Whether to require exact match or allow prefix matching

        """
        self.pattern = pattern
        self.exact_match = exact_match

    def matches(self, event: TestAPIXEvent) -> bool:
        """Check if event type matches the filter pattern."""
        if self.exact_match:
            return event.event_type == self.pattern
        return event.event_type.startswith(self.pattern)


class PriorityFilter(EventFilter):
    """Filter events by minimum priority level."""

    def __init__(self, min_priority: EventPriority) -> None:
        """Initialize priority filter.

        Args:
        ----
            min_priority: Minimum priority level to match

        """
        self.min_priority = min_priority

    def matches(self, event: TestAPIXEvent) -> bool:
        """Check if event priority meets minimum requirement."""
        return event.priority.value >= self.min_priority.value


class SourceFilter(EventFilter):
    """Filter events by source pattern."""

    def __init__(self, source_pattern: str) -> None:
        """Initialize source filter.

        Args:
        ----
            source_pattern: Source pattern to match

        """
        self.source_pattern = source_pattern

    def matches(self, event: TestAPIXEvent) -> bool:
        """Check if event source matches the filter pattern."""
        if event.source is None:
            return False
        return self.source_pattern in event.source


class DataFilter(EventFilter):
    """Filter events by data content."""

    def __init__(self, key: str, value: Any = None, exists_only: bool = False) -> None:
        """Initialize data filter.

        Args:
        ----
            key: Data key to check
            value: Expected value (if None and exists_only=False, any value matches)
            exists_only: If True, only check if key exists regardless of value

        """
        self.key = key
        self.value = value
        self.exists_only = exists_only

    def matches(self, event: TestAPIXEvent) -> bool:
        """Check if event data matches the filter criteria."""
        if self.key not in event.data:
            return False

        if self.exists_only:
            return True

        if self.value is None:
            return True

        return bool(event.data[self.key] == self.value)


@dataclass
class EventSubscription:
    """Represents a subscription to events.

    Subscriptions track handlers, filters, and metadata about
    event listening relationships.
    """

    handler: EventHandler
    event_filter: EventFilter | None = None
    subscription_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    call_count: int = 0
    last_called: datetime | None = None
    is_async: bool = False

    def __post_init__(self) -> None:
        """Determine if handler is async after initialization."""
        self.is_async = asyncio.iscoroutinefunction(self.handler)

    def matches_event(self, event: TestAPIXEvent) -> bool:
        """Check if this subscription should handle the given event."""
        if self.event_filter is None:
            return True
        return self.event_filter.matches(event)

    def update_stats(self) -> None:
        """Update call statistics for this subscription."""
        self.call_count += 1
        self.last_called = datetime.now()


class EventBus:
    """Central event bus for TestAPIX event system.

    The event bus manages event publication, subscription, and delivery.
    It supports both synchronous and asynchronous event handling with
    filtering, priority-based processing, and error handling.
    """

    def __init__(self, name: str = "default") -> None:
        """Initialize the event bus.

        Args:
        ----
            name: Name identifier for this event bus instance

        """
        self.name = name
        self._subscriptions: dict[str, list[EventSubscription]] = {}
        self._global_subscriptions: list[EventSubscription] = []
        self._event_history: list[TestAPIXEvent] = []
        self._max_history = 1000
        self._logger = logging.getLogger(f"{__name__}.{name}")
        self._lock = threading.RLock()
        self._stats = {
            "events_published": 0,
            "events_handled": 0,
            "handler_errors": 0,
        }

    def subscribe(
        self,
        event_type: str | None,
        handler: EventHandler,
        event_filter: EventFilter | None = None,
    ) -> str:
        """Subscribe to events of a specific type or all events.

        Args:
        ----
            event_type: Type of events to subscribe to, or None for all events
            handler: Function to call when matching events occur
            event_filter: Optional filter for more granular event selection

        Returns:
        -------
            Subscription ID that can be used to unsubscribe

        Raises:
        ------
            EventError: If subscription fails

        """
        try:
            subscription = EventSubscription(
                handler=handler,
                event_filter=event_filter,
            )

            with self._lock:
                if event_type is None:
                    # Global subscription - receives all events
                    self._global_subscriptions.append(subscription)
                else:
                    # Type-specific subscription
                    if event_type not in self._subscriptions:
                        self._subscriptions[event_type] = []
                    self._subscriptions[event_type].append(subscription)

            self._logger.debug(
                f"Added subscription {subscription.subscription_id} for event type: {event_type}"
            )
            return subscription.subscription_id

        except Exception as e:
            raise EventError(
                f"Failed to subscribe to events: {e}", event_type=event_type
            ) from e

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events using subscription ID.

        Args:
        ----
            subscription_id: ID returned from subscribe()

        Returns:
        -------
            True if subscription was found and removed, False otherwise

        """
        with self._lock:
            # Check global subscriptions
            for i, sub in enumerate(self._global_subscriptions):
                if sub.subscription_id == subscription_id:
                    self._global_subscriptions.pop(i)
                    self._logger.debug(f"Removed global subscription {subscription_id}")
                    return True

            # Check type-specific subscriptions
            for event_type, subscriptions in self._subscriptions.items():
                for i, sub in enumerate(subscriptions):
                    if sub.subscription_id == subscription_id:
                        subscriptions.pop(i)
                        # Clean up empty subscription lists
                        if not subscriptions:
                            del self._subscriptions[event_type]
                        self._logger.debug(
                            f"Removed subscription {subscription_id} for {event_type}"
                        )
                        return True

        return False

    def publish(self, event: TestAPIXEvent) -> None:
        """Publish an event to all matching subscribers.

        Args:
        ----
            event: Event to publish

        Raises:
        ------
            EventError: If event publication fails

        """
        try:
            with self._lock:
                self._stats["events_published"] += 1

                # Add to history
                self._add_to_history(event)

                # Get all matching subscriptions
                matching_subscriptions = self._get_matching_subscriptions(event)

                # Sort by priority if handler supports it
                matching_subscriptions.sort(
                    key=lambda sub: getattr(sub.handler, "_priority", 0), reverse=True
                )

            # Handle event delivery
            for subscription in matching_subscriptions:
                self._handle_event_delivery(event, subscription)

            self._logger.debug(
                f"Published event {event.event_type} to {len(matching_subscriptions)} handlers"
            )

        except Exception as e:
            raise EventError(
                f"Failed to publish event: {e}", event_type=event.event_type
            ) from e

    async def publish_async(self, event: TestAPIXEvent) -> None:
        """Publish an event asynchronously to all matching subscribers.

        Args:
        ----
            event: Event to publish

        Raises:
        ------
            EventError: If event publication fails

        """
        try:
            with self._lock:
                self._stats["events_published"] += 1

                # Add to history
                self._add_to_history(event)

                # Get all matching subscriptions
                matching_subscriptions = self._get_matching_subscriptions(event)

                # Sort by priority if handler supports it
                matching_subscriptions.sort(
                    key=lambda sub: getattr(sub.handler, "_priority", 0), reverse=True
                )

            # Handle event delivery asynchronously
            await self._handle_event_delivery_async(event, matching_subscriptions)

            self._logger.debug(
                f"Published event {event.event_type} async to {len(matching_subscriptions)} handlers"
            )

        except Exception as e:
            raise EventError(
                f"Failed to publish event async: {e}", event_type=event.event_type
            ) from e

    def emit(
        self,
        event_type: str,
        data: dict[str, Any],
        source: str | None = None,
        priority: EventPriority = EventPriority.NORMAL,
        correlation_id: str | None = None,
    ) -> None:
        """Convenience method to create and publish an event.

        Args:
        ----
            event_type: Type identifier for the event
            data: Event data payload
            source: Optional source identifier
            priority: Event priority level
            correlation_id: Optional correlation ID for event tracking

        """
        event = TestAPIXEvent(
            event_type=event_type,
            data=data,
            source=source,
            priority=priority,
            correlation_id=correlation_id,
        )
        self.publish(event)

    async def emit_async(
        self,
        event_type: str,
        data: dict[str, Any],
        source: str | None = None,
        priority: EventPriority = EventPriority.NORMAL,
        correlation_id: str | None = None,
    ) -> None:
        """Convenience method to create and publish an event asynchronously.

        Args:
        ----
            event_type: Type identifier for the event
            data: Event data payload
            source: Optional source identifier
            priority: Event priority level
            correlation_id: Optional correlation ID for event tracking

        """
        event = TestAPIXEvent(
            event_type=event_type,
            data=data,
            source=source,
            priority=priority,
            correlation_id=correlation_id,
        )
        await self.publish_async(event)

    def get_stats(self) -> dict[str, Any]:
        """Get event bus statistics."""
        with self._lock:
            return {
                **self._stats,
                "active_subscriptions": sum(
                    len(subs) for subs in self._subscriptions.values()
                )
                + len(self._global_subscriptions),
                "event_types": list(self._subscriptions.keys()),
                "history_size": len(self._event_history),
            }

    def get_event_history(self, limit: int | None = None) -> list[TestAPIXEvent]:
        """Get recent event history.

        Args:
        ----
            limit: Maximum number of events to return (None for all)

        Returns:
        -------
            List of recent events, most recent first

        """
        with self._lock:
            history = list(reversed(self._event_history))
            if limit is not None:
                history = history[:limit]
            return history

    def clear_history(self) -> None:
        """Clear event history."""
        with self._lock:
            self._event_history.clear()

    def clear_subscriptions(self) -> None:
        """Remove all subscriptions."""
        with self._lock:
            self._subscriptions.clear()
            self._global_subscriptions.clear()

    def _get_matching_subscriptions(
        self, event: TestAPIXEvent
    ) -> list[EventSubscription]:
        """Get all subscriptions that match the given event."""
        matching = []

        # Add global subscriptions that match
        for sub in self._global_subscriptions:
            if sub.matches_event(event):
                matching.append(sub)

        # Add type-specific subscriptions that match
        if event.event_type in self._subscriptions:
            for sub in self._subscriptions[event.event_type]:
                if sub.matches_event(event):
                    matching.append(sub)

        return matching

    def _handle_event_delivery(
        self, event: TestAPIXEvent, subscription: EventSubscription
    ) -> None:
        """Handle delivery of an event to a single subscription."""
        try:
            subscription.update_stats()

            if subscription.is_async:
                # For async handlers in sync context, we'll run them in thread pool
                # This is a simplified approach - in production you might want more sophisticated handling
                self._logger.warning(
                    f"Async handler {subscription.handler} called in sync context for event {event.event_type}"
                )
                return

            # Call sync handler
            subscription.handler(event)
            self._stats["events_handled"] += 1

        except Exception as e:
            self._stats["handler_errors"] += 1
            self._logger.error(
                f"Handler {subscription.handler} failed for event {event.event_type}: {e}",
                exc_info=True,
            )

    async def _handle_event_delivery_async(
        self, event: TestAPIXEvent, subscriptions: list[EventSubscription]
    ) -> None:
        """Handle async delivery of an event to multiple subscriptions."""
        tasks: list[asyncio.Task[Any]] = []

        for subscription in subscriptions:
            try:
                subscription.update_stats()

                if subscription.is_async:
                    # Create async task - cast to ensure proper type
                    handler_coro = subscription.handler(event)
                    if asyncio.iscoroutine(handler_coro):
                        task: asyncio.Task[Any] = asyncio.create_task(handler_coro)
                        tasks.append(task)
                else:
                    # Run sync handler in thread pool - run_in_executor returns a Future
                    async def run_sync_handler(
                        subscription: EventSubscription = subscription,
                    ) -> None:
                        await asyncio.get_event_loop().run_in_executor(
                            None, subscription.handler, event
                        )

                    task = asyncio.create_task(run_sync_handler())
                    tasks.append(task)

            except Exception as e:
                self._stats["handler_errors"] += 1
                self._logger.error(
                    f"Failed to create task for handler {subscription.handler}: {e}",
                    exc_info=True,
                )

        # Wait for all tasks to complete
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Count successful handlers and log errors
            for result in results:
                if isinstance(result, Exception):
                    self._stats["handler_errors"] += 1
                    self._logger.error(
                        f"Async handler failed for event {event.event_type}: {result}",
                        exc_info=result,
                    )
                else:
                    self._stats["events_handled"] += 1

    def _add_to_history(self, event: TestAPIXEvent) -> None:
        """Add event to history, maintaining size limit."""
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)


# Global event bus instance
global_event_bus = EventBus("global")


def event_handler(
    event_type: str | None = None,
    event_filter: EventFilter | None = None,
    priority: int = 0,
    event_bus: EventBus = global_event_bus,
) -> Callable[[EventHandler], EventHandler]:
    """Decorator for registering event handlers.

    Args:
    ----
        event_type: Type of events to handle (None for all events)
        event_filter: Optional filter for event selection
        priority: Handler priority (higher numbers run first)
        event_bus: Event bus to register with

    Returns:
    -------
        Decorated handler function

    """

    def decorator(handler: EventHandler) -> EventHandler:
        # Store priority as function attribute
        handler._priority = priority  # type: ignore

        # Register handler with event bus
        subscription_id = event_bus.subscribe(
            event_type=event_type,
            handler=handler,
            event_filter=event_filter,
        )

        # Store subscription ID for potential cleanup
        handler._subscription_id = subscription_id  # type: ignore

        return handler

    return decorator


@contextmanager
def event_context(event_bus: EventBus = global_event_bus) -> Any:
    """Context manager for temporary event subscriptions.

    Args:
    ----
        event_bus: Event bus to use for subscriptions

    Yields:
    ------
        Event bus instance for making subscriptions

    """
    subscriptions = []

    class ContextEventBus:
        def subscribe(
            self,
            event_type: str | None,
            handler: EventHandler,
            event_filter: EventFilter | None = None,
        ) -> str:
            sub_id = event_bus.subscribe(event_type, handler, event_filter)
            subscriptions.append(sub_id)
            return sub_id

        def __getattr__(self, name: str) -> Any:
            return getattr(event_bus, name)

    try:
        yield ContextEventBus()
    finally:
        # Clean up subscriptions
        for sub_id in subscriptions:
            event_bus.unsubscribe(sub_id)


@asynccontextmanager
async def async_event_context(
    event_bus: EventBus = global_event_bus,
) -> AsyncGenerator[EventBus, None]:
    """Async context manager for temporary event subscriptions.

    Args:
    ----
        event_bus: Event bus to use for subscriptions

    Yields:
    ------
        Event bus instance for making subscriptions

    """
    subscriptions = []

    class ContextEventBus:
        def subscribe(
            self,
            event_type: str | None,
            handler: EventHandler,
            event_filter: EventFilter | None = None,
        ) -> str:
            sub_id = event_bus.subscribe(event_type, handler, event_filter)
            subscriptions.append(sub_id)
            return sub_id

        def __getattr__(self, name: str) -> Any:
            return getattr(event_bus, name)

    try:
        yield ContextEventBus()  # type: ignore
    finally:
        # Clean up subscriptions
        for sub_id in subscriptions:
            event_bus.unsubscribe(sub_id)
