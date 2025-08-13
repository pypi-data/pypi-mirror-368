"""
Notification Hub

"""

import asyncio
import json
import logging
import time
import uuid
from asyncio import CancelledError
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

import zmq
import zmq.asyncio

from .event import NotificationEvent

from . import DEFAULT_NH_COLLECTION_PORT
from . import DEFAULT_NH_PUBLISH_PORT

NOTIFY_HUB_COLLECTOR = f"tcp://localhost:{DEFAULT_NH_COLLECTION_PORT}"
NOTIFY_HUB_PUBLISHER = f"tcp://localhost:{DEFAULT_NH_PUBLISH_PORT}"


class AsyncEventPublisher:
    """Reusable event publisher component"""

    def __init__(self, hub_address: str = NOTIFY_HUB_COLLECTOR):
        self.hub_address = hub_address
        self.context = zmq.asyncio.Context()
        self.publisher = None
        self._connected = False
        self.logger = logging.getLogger("event-pub")

    async def connect(self):
        """Connect to the notification hub"""
        if not self._connected:
            self.publisher = self.context.socket(zmq.PUSH)
            self.publisher.connect(self.hub_address)
            await asyncio.sleep(0.1)  # Allow connection to establish
            self._connected = True
            self.logger.info(f"Connected to hub at {self.hub_address}")

    async def publish(self, event: NotificationEvent):
        """Publish an event"""
        if not self._connected:
            await self.connect()

        message = {
            "event_type": event.event_type,
            "source_service": event.source_service,
            "data": event.data,
            "timestamp": event.timestamp,
            "correlation_id": event.correlation_id or str(uuid.uuid4()),
        }

        await self.publisher.send(json.dumps(message).encode())
        self.logger.debug(f"Published: {event.event_type}")

    async def close(self):
        """Clean shutdown"""
        if self._connected:
            self.publisher.close()
            self._connected = False


class AsyncEventSubscriber:
    """Reusable event subscriber component"""

    def __init__(self, subscriptions: List[str], hub_address: str = NOTIFY_HUB_PUBLISHER):
        self.subscriptions = subscriptions
        self.hub_address = hub_address
        self.context = zmq.asyncio.Context()
        self.subscriber = None
        self.handlers: Dict[str, Callable] = {}
        self.running = False
        self.logger = logging.getLogger("event-sub")

    async def connect(self):
        """Connect to the notification hub"""
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect(self.hub_address)

        # Subscribe to specific event types
        for event_type in self.subscriptions:
            self.subscriber.setsockopt(zmq.SUBSCRIBE, event_type.encode())
            self.logger.info(f"Subscribed to: {event_type}")

    def register_handler(self, event_type: str, handler: Callable):
        """Register a handler for an event type"""
        self.handlers[event_type] = handler

    async def start_listening(self):
        """Start listening for events"""
        if not self.subscriber:
            await self.connect()

        self.running = True
        self.logger.info("Started listening for events")

        while self.running:
            try:
                if await self.subscriber.poll(timeout=1000):
                    topic, message_bytes = await self.subscriber.recv_multipart()

                    event_type = topic.decode()
                    event_data = json.loads(message_bytes.decode())

                    await self._handle_event(event_type, event_data)

                await asyncio.sleep(0.001)

            except Exception as exc:
                self.logger.error(f"Error receiving event: {exc}")
                await asyncio.sleep(1)
            except CancelledError:
                break

    async def _handle_event(self, event_type: str, event_data: Dict):
        """Handle received event"""
        handler = self.handlers.get(event_type)

        if handler:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_data)
                else:
                    await asyncio.get_event_loop().run_in_executor(None, handler, event_data)
            except Exception as e:
                self.logger.error(f"Error handling {event_type}: {e}")
        else:
            self.logger.warning(f"No handler registered for {event_type}")

    async def stop(self):
        """Stop listening"""
        self.running = False
        if self.subscriber:
            self.subscriber.close()


class ServiceMessaging:
    """Convenience wrapper that combines publisher and subscriber."""

    def __init__(self, service_name: str, subscriptions: List[str] | None = None):
        self.service_name = service_name
        self.publisher = AsyncEventPublisher()
        self.subscriber = AsyncEventSubscriber(subscriptions or []) if subscriptions else None

    async def publish_event(self, event_type: str, data: Dict[Any, Any], correlation_id: Optional[str] = None):
        """Publish an event"""
        event = NotificationEvent(
            event_type=event_type,
            source_service=self.service_name,
            data=data,
            timestamp=time.time(),
            correlation_id=correlation_id,
        )
        await self.publisher.publish(event)

    def register_handler(self, event_type: str, handler: Callable):
        """Register event handler"""
        if self.subscriber:
            self.subscriber.register_handler(event_type, handler)

    async def start_listening(self):
        """Start listening for events"""
        if self.subscriber:
            await self.subscriber.start_listening()

    async def close(self):
        """Clean shutdown"""
        await self.publisher.close()
        if self.subscriber:
            await self.subscriber.stop()
