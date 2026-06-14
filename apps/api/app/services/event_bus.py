"""
Event Bus — in-memory pub/sub for SSE streaming.
Sessions publish events; SSE endpoints subscribe per session_id.

Hardening changes (Step 7.1):
- asyncio.Lock guards all mutations of _subscribers to prevent
  concurrent modification bugs under multiple simultaneous users.
- Queues are unbounded (maxsize=0) so fast publishers never silently
  drop events on slow connections.
- close_session sends the sentinel WITHOUT removing the list first
  so that the subscriber's finally-block can cleanly remove itself.
  The list is pruned only after all queued sentinels are placed.
- _cleanup_session removes the empty list key when the last
  subscriber departs, preventing ghost keys from leaking memory.
- Heartbeat is re-yielded after every 30-second idle window so the
  SSE connection stays alive for long-running graph executions.
- Event sequence numbers are included for ordering verification.
"""
import asyncio
import json
import itertools
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, List, Optional

# Per-process monotonic sequence counter (not per-session intentionally:
# gives a global ordering across overlapping sessions for debugging).
_SEQ_COUNTER = itertools.count(1)

_SENTINEL = None  # type: ignore[assignment]


class EventBus:
    """
    In-memory async event bus for real-time SSE streaming.

    Thread / coroutine safety:
    All mutations of _subscribers are protected by _lock.
    Callers must hold _lock before reading or writing the dict.
    """

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}
        self._lock = asyncio.Lock()

    # ──────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────

    async def _add_subscriber(self, session_id: str, queue: asyncio.Queue) -> None:
        async with self._lock:
            self._subscribers.setdefault(session_id, []).append(queue)

    async def _remove_subscriber(self, session_id: str, queue: asyncio.Queue) -> None:
        async with self._lock:
            queues = self._subscribers.get(session_id)
            if queues is None:
                return
            try:
                queues.remove(queue)
            except ValueError:
                pass
            # Prune ghost key once no subscribers remain
            if not queues:
                self._subscribers.pop(session_id, None)

    # ──────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────

    async def publish(self, session_id: str, event: str, data: Any) -> None:
        """Publish an event to all subscribers of a session.

        Safe to call from background tasks concurrently with subscribe/
        close_session.  Events are never dropped (unbounded queues).
        """
        payload: Dict[str, Any] = {
            "event": event,
            "data": data,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "seq": next(_SEQ_COUNTER),
        }
        async with self._lock:
            queues = list(self._subscribers.get(session_id, []))

        for queue in queues:
            await queue.put(payload)

    async def subscribe(
        self, session_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Subscribe to events for a session.

        Yields events as they arrive.  Sends a heartbeat every 30 s of
        idle time so the TCP connection is not closed by load-balancers.
        Exits cleanly when close_session() sends the sentinel, or when
        the caller cancels the coroutine (browser disconnect).
        """
        # Unbounded queue: producers never block or drop events.
        queue: asyncio.Queue = asyncio.Queue()
        await self._add_subscriber(session_id, queue)
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    if event is _SENTINEL:
                        # Session closed server-side — exit cleanly.
                        break
                    yield event
                except asyncio.TimeoutError:
                    # 30-second idle — send heartbeat then keep waiting.
                    yield {
                        "event": "heartbeat",
                        "data": {"session_id": session_id},
                        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                        "seq": next(_SEQ_COUNTER),
                    }
        except asyncio.CancelledError:
            # Browser disconnected — absorb so finally can run.
            pass
        finally:
            await self._remove_subscriber(session_id, queue)

    async def close_session(self, session_id: str) -> None:
        """Signal all current subscribers that the session is done.

        Sends the sentinel to every queue *before* removing the list,
        so that subscribe()'s finally-block can still find and remove
        itself via _remove_subscriber.
        """
        async with self._lock:
            queues = list(self._subscribers.get(session_id, []))

        for queue in queues:
            await queue.put(_SENTINEL)
        # Do NOT pop the session here — subscribers clean themselves up
        # via _remove_subscriber in their finally blocks, which will
        # prune the list when it becomes empty.

    def subscriber_count(self, session_id: str) -> int:
        """Return the number of active subscribers (useful for tests/metrics)."""
        return len(self._subscribers.get(session_id, []))

    def active_sessions(self) -> List[str]:
        """Return list of session IDs with at least one subscriber."""
        return list(self._subscribers.keys())
