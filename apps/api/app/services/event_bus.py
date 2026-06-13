"""
Event Bus — in-memory pub/sub for SSE streaming.
Sessions publish events, SSE endpoints subscribe per session_id.
"""
import asyncio
import json
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, List, Set


class EventBus:
    """In-memory async event bus for real-time SSE streaming."""

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[asyncio.Queue[Dict[str, Any] | None]]] = {}

    def _get_queues(self, session_id: str) -> List[asyncio.Queue[Dict[str, Any] | None]]:
        return self._subscribers.setdefault(session_id, [])

    async def publish(self, session_id: str, event: str, data: Any) -> None:
        """Publish an event to all subscribers of a session."""
        payload = {
            "event": event,
            "data": data,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        }
        queues = self._get_queues(session_id)
        for queue in queues:
            await queue.put(payload)

    async def subscribe(self, session_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Subscribe to events for a session. Yields events as they arrive."""
        queue: asyncio.Queue[Dict[str, Any] | None] = asyncio.Queue(maxsize=100)
        self._get_queues(session_id).append(queue)
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    if event is None:
                        break
                    yield event
                except asyncio.TimeoutError:
                    # Send heartbeat on timeout then continue waiting
                    yield {
                        "event": "heartbeat",
                        "data": {"session_id": session_id},
                        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                    }
        except asyncio.CancelledError:
            pass
        finally:
            queues = self._get_queues(session_id)
            if queue in queues:
                queues.remove(queue)

    async def close_session(self, session_id: str) -> None:
        """Signal all subscribers that the session is done."""
        queues = self._get_queues(session_id)
        for queue in queues:
            await queue.put(None)
        self._subscribers.pop(session_id, None)
