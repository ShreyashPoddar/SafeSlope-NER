"""
ResiliNER / SafeSlope-NER - Real-Time Comms Event Stream
Member 6: Communications & Bot Developer

Provides an in-memory pub/sub broadcaster for Server-Sent Events (SSE)
and WebSockets to feed real-time incident updates to Member 5's GIS dashboard.
"""

import asyncio
import json
from typing import AsyncGenerator, Set


class CommsEventBroadcaster:
    def __init__(self):
        self._listeners: Set[asyncio.Queue] = set()

    async def subscribe(self) -> AsyncGenerator[str, None]:
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._listeners.add(queue)
        try:
            while True:
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"data: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    # Send standard SSE keepalive comment to keep browser connection warm
                    yield ": ping\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            if queue in self._listeners:
                self._listeners.remove(queue)

    def publish_nowait(self, event_type: str, payload: dict):
        """Broadcast an event payload to all connected subscribers."""
        event_obj = {
            "type": event_type,
            "payload": payload,
        }
        for q in list(self._listeners):
            try:
                q.put_nowait(event_obj)
            except asyncio.QueueFull:
                pass


broadcaster = CommsEventBroadcaster()
