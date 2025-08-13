import asyncio
import json
import logging
import time

import zmq
import zmq.asyncio

from egse.settings import Settings
from .event import NotificationEvent

SETTINGS = Settings.load("Notify Hub")

DEFAULT_COLLECTOR_PORT = SETTINGS.get("COLLECTOR_PORT", 0)
DEFAULT_PUBLISHER_PORT = SETTINGS.get("PUBLISHER_PORT", 0)


class AsyncNotificationHub:
    def __init__(self):
        # Use asyncio-compatible ZeroMQ context
        self.context = zmq.asyncio.Context()

        # Receive events from services (PULL socket for load balancing)
        self.collector = self.context.socket(zmq.PULL)
        self.collector.bind(f"tcp://*:{DEFAULT_COLLECTOR_PORT}")

        # Publish events to subscribers (PUB socket for fan-out)
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind(f"tcp://*:{DEFAULT_PUBLISHER_PORT}")

        # Track statistics
        self.stats = {"events_received": 0, "events_published": 0, "active_subscribers": 0}

        self.running = False
        self.logger = logging.getLogger("notification-hub")

    async def start(self):
        """Start the notification hub"""
        self.running = True
        self.logger.info("Starting Async Notification Hub...")

        # Start concurrent tasks
        tasks = [
            asyncio.create_task(self.event_collector()),
            asyncio.create_task(self.stats_reporter()),
            asyncio.create_task(self.health_check()),
        ]

        try:
            # Run all tasks concurrently
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            self.logger.info("Shutting down...")
            await self.stop()

    async def event_collector(self):
        """Main event collection loop"""
        while self.running:
            try:
                # Receive event from any service (non-blocking with timeout)
                if await self.collector.poll(timeout=1000):
                    message_bytes = await self.collector.recv()
                    message = json.loads(message_bytes.decode())

                    event = NotificationEvent(
                        event_type=message["event_type"],
                        source_service=message["source_service"],
                        data=message["data"],
                        timestamp=message.get("timestamp", time.time()),
                        correlation_id=message.get("correlation_id"),
                    )

                    self.logger.info(f"Received: {event.event_type} from {event.source_service}")
                    self.stats["events_received"] += 1

                    await self.publish_event(event)

            except asyncio.CancelledError:
                self.running = False
            except Exception as exc:
                self.logger.error(f"Error in event collector: {exc}", exc_info=True)
                # Why waiting 1s here?
                # - Is this to prevent overloading the logger when there is a serious problem
                # - Will this improve when we get more experience with the NotifyHub?
                await asyncio.sleep(1.0)

    async def publish_event(self, event: NotificationEvent):
        """Publish event to all subscribers"""
        try:
            message = {
                "event_type": event.event_type,
                "source_service": event.source_service,
                "data": event.data,
                "timestamp": event.timestamp,
                "correlation_id": event.correlation_id,
            }

            await self.publisher.send_multipart(
                [
                    event.event_type.encode(),  # Topic for filtering
                    json.dumps(message).encode(),  # Event data
                ]
            )

            self.stats["events_published"] += 1
            self.logger.debug(f"Published: {event.event_type}")

        except Exception as exc:
            self.logger.error(f"Error publishing event: {exc}")

    async def stats_reporter(self):
        """Periodically report statistics"""
        while self.running:
            try:
                await asyncio.sleep(30)
                self.logger.info(f"Stats: {self.stats}")
            except asyncio.CancelledError:
                self.running = False

    async def health_check(self):
        """Simple health check endpoint simulation"""
        while self.running:
            try:
                await asyncio.sleep(10)

                # Implement actual health checks here

                self.logger.debug("Health check: OK")
            except asyncio.CancelledError:
                self.running = False

    async def stop(self):
        """Graceful shutdown"""
        if self.running:
            self.running = False
            self.collector.close()
            self.publisher.close()
            self.context.term()


# Usage
async def run_hub():
    hub = AsyncNotificationHub()
    await hub.start()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] %(levelname)-8s %(name)-20s %(lineno)5d:%(module)-20s %(message)s",
    )
    try:
        asyncio.run(run_hub())
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt received for NotifyHub, terminating...")
