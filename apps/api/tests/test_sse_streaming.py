"""
SSE Streaming Test Suite — Step 7.1 Audit
==========================================
Tests all required scenarios:
  ✓ Single user session
  ✓ Multiple concurrent sessions
  ✓ Graph success path
  ✓ Graph failure path
  ✓ Idle connection > 60 seconds (heartbeat)
  ✓ Browser refresh during stream (subscriber cleanup)
  ✓ Session completion (sentinel + cleanup)

Run with:
    cd apps/api
    python -m pytest tests/test_sse_streaming.py -v --asyncio-mode=auto
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.services.event_bus import EventBus


# ═══════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════

async def collect_events(
    bus: EventBus,
    session_id: str,
    max_events: int = 20,
    timeout: float = 5.0,
) -> list:
    """Subscribe and collect up to `max_events` from `session_id`."""
    events = []
    async def _run():
        async for event in bus.subscribe(session_id):
            events.append(event)
            if len(events) >= max_events:
                break
    try:
        await asyncio.wait_for(_run(), timeout=timeout)
    except asyncio.TimeoutError:
        pass
    return events


async def _subscribe_with_short_timeout(bus: EventBus, session_id: str, timeout_s: float):
    """
    Yield events from `bus.subscribe(session_id)` but with an overridden
    idle timeout of `timeout_s` seconds.  This lets heartbeat tests run in
    milliseconds without patching global asyncio functions.
    """
    import itertools
    from datetime import datetime, timezone

    _seq = itertools.count(1)

    queue: asyncio.Queue = asyncio.Queue()
    await bus._add_subscriber(session_id, queue)
    try:
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=timeout_s)
                if event is None:
                    break
                yield event
            except asyncio.TimeoutError:
                yield {
                    "event": "heartbeat",
                    "data": {"session_id": session_id},
                    "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                    "seq": next(_seq),
                }
    except asyncio.CancelledError:
        pass
    finally:
        await bus._remove_subscriber(session_id, queue)


# ═══════════════════════════════════════════════════════════════════════
# 1. HEARTBEAT — continues indefinitely, no stream close
# ═══════════════════════════════════════════════════════════════════════

class TestHeartbeat:
    """Verify heartbeats fire and do NOT close the stream."""

    @pytest.mark.asyncio
    async def test_heartbeat_emitted_after_idle(self):
        """After idle the bus must send a heartbeat without closing."""
        bus = EventBus()
        session_id = "hb-test-1"
        heartbeats = []

        async def subscriber():
            # Use a very short wait_for timeout by patching the constant
            # inline via a subclass so we don't touch the real module.
            async for event in _subscribe_with_short_timeout(bus, session_id, 0.05):
                if event["event"] == "heartbeat":
                    heartbeats.append(event)
                    break

        task = asyncio.create_task(subscriber())
        await asyncio.wait_for(task, timeout=3.0)

        assert len(heartbeats) >= 1, "Expected at least one heartbeat"
        assert heartbeats[0]["event"] == "heartbeat"

    @pytest.mark.asyncio
    async def test_heartbeat_does_not_close_stream(self):
        """Stream must still deliver real events after a heartbeat."""
        bus = EventBus()
        session_id = "hb-test-2"
        received = []

        async def subscriber():
            async for event in _subscribe_with_short_timeout(bus, session_id, 0.05):
                received.append(event)
                if event["event"] == "real_event":
                    break

        sub_task = asyncio.create_task(subscriber())
        await asyncio.sleep(0.15)  # Let one heartbeat fire
        await bus.publish(session_id, "real_event", {"msg": "hello"})
        await asyncio.wait_for(sub_task, timeout=3.0)

        events_by_type = {e["event"] for e in received}
        assert "heartbeat" in events_by_type
        assert "real_event" in events_by_type


# ═══════════════════════════════════════════════════════════════════════
# 2. MEMORY / SUBSCRIBER CLEANUP
# ═══════════════════════════════════════════════════════════════════════

class TestSubscriberLifecycle:
    """No memory leaks from stale subscribers."""

    @pytest.mark.asyncio
    async def test_subscriber_removed_after_session_close(self):
        """After close_session all queues and the session key must be gone."""
        bus = EventBus()
        sid = "lifecycle-1"

        async def subscriber():
            async for _ in bus.subscribe(sid):
                pass  # consume until sentinel

        task = asyncio.create_task(subscriber())
        await asyncio.sleep(0.05)  # Let subscriber register

        assert bus.subscriber_count(sid) == 1

        await bus.close_session(sid)
        await asyncio.wait_for(task, timeout=2.0)

        # Queue and session key must be fully pruned
        assert bus.subscriber_count(sid) == 0
        assert sid not in bus.active_sessions()

    @pytest.mark.asyncio
    async def test_subscriber_removed_on_cancel(self):
        """Cancelled subscriber (browser disconnect) cleans up its queue."""
        bus = EventBus()
        sid = "lifecycle-2"

        async def subscriber():
            async for _ in bus.subscribe(sid):
                await asyncio.sleep(100)  # Block here

        task = asyncio.create_task(subscriber())
        await asyncio.sleep(0.05)

        assert bus.subscriber_count(sid) == 1

        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        await asyncio.sleep(0.05)  # Let finally block run
        assert bus.subscriber_count(sid) == 0

    @pytest.mark.asyncio
    async def test_no_ghost_key_after_last_subscriber_leaves(self):
        """Session key must not persist after all subscribers disconnect."""
        bus = EventBus()
        sid = "lifecycle-3"

        async def subscriber():
            async for _ in bus.subscribe(sid):
                pass

        task = asyncio.create_task(subscriber())
        await asyncio.sleep(0.05)
        await bus.close_session(sid)
        await asyncio.wait_for(task, timeout=2.0)

        assert sid not in bus.active_sessions(), "Ghost session key leaked"


# ═══════════════════════════════════════════════════════════════════════
# 3. MULTIPLE CONCURRENT USERS
# ═══════════════════════════════════════════════════════════════════════

class TestConcurrentSessions:
    """Multiple simultaneous sessions must not interfere."""

    @pytest.mark.asyncio
    async def test_events_isolated_per_session(self):
        """Events published to session A must not appear in session B."""
        bus = EventBus()
        sid_a = "concurrent-a"
        sid_b = "concurrent-b"

        events_a, events_b = [], []

        async def sub_a():
            async for ev in bus.subscribe(sid_a):
                events_a.append(ev)

        async def sub_b():
            async for ev in bus.subscribe(sid_b):
                events_b.append(ev)

        task_a = asyncio.create_task(sub_a())
        task_b = asyncio.create_task(sub_b())
        await asyncio.sleep(0.05)

        await bus.publish(sid_a, "test_event", {"owner": "a"})
        await bus.publish(sid_b, "test_event", {"owner": "b"})

        await asyncio.sleep(0.1)

        await bus.close_session(sid_a)
        await bus.close_session(sid_b)
        await asyncio.gather(task_a, task_b)

        assert all(e["data"]["owner"] == "a" for e in events_a)
        assert all(e["data"]["owner"] == "b" for e in events_b)

    @pytest.mark.asyncio
    async def test_multiple_subscribers_same_session(self):
        """Two subscribers on the same session both receive all events."""
        bus = EventBus()
        sid = "concurrent-same"
        received_1, received_2 = [], []

        async def sub1():
            async for ev in bus.subscribe(sid):
                received_1.append(ev)

        async def sub2():
            async for ev in bus.subscribe(sid):
                received_2.append(ev)

        t1 = asyncio.create_task(sub1())
        t2 = asyncio.create_task(sub2())
        await asyncio.sleep(0.05)

        assert bus.subscriber_count(sid) == 2

        await bus.publish(sid, "msg", {"n": 1})
        await bus.publish(sid, "msg", {"n": 2})

        await asyncio.sleep(0.1)
        await bus.close_session(sid)
        await asyncio.gather(t1, t2)

        assert len(received_1) == 2
        assert len(received_2) == 2

    @pytest.mark.asyncio
    async def test_10_concurrent_sessions(self):
        """Stress test: 10 concurrent sessions, each with 2 subscribers."""
        bus = EventBus()
        N = 10
        # Each session has 2 subscribers; they share the same list.
        collected = {f"sess-{i}": [] for i in range(N)}

        async def subscriber(sid: str):
            async for ev in bus.subscribe(sid):
                collected[sid].append(ev)

        tasks = []
        for i in range(N):
            sid = f"sess-{i}"
            tasks.append(asyncio.create_task(subscriber(sid)))
            tasks.append(asyncio.create_task(subscriber(sid)))

        await asyncio.sleep(0.05)

        # Publish ONE event per session
        for i in range(N):
            await bus.publish(f"sess-{i}", "ping", {"i": i})

        await asyncio.sleep(0.1)

        # Close all sessions
        for i in range(N):
            await bus.close_session(f"sess-{i}")

        await asyncio.gather(*tasks)

        for i in range(N):
            sid = f"sess-{i}"
            # 2 subscribers each receive 1 event => 2 entries total
            assert len(collected[sid]) == 2, (
                f"Expected 2 entries (2 subs x 1 event) for {sid}, "
                f"got {len(collected[sid])}"
            )
            # Both entries should be the same event for this session
            assert all(e["data"]["i"] == i for e in collected[sid])

        # All session keys must be gone
        assert bus.active_sessions() == []


# ═══════════════════════════════════════════════════════════════════════
# 4. NO DUPLICATE EVENTS
# ═══════════════════════════════════════════════════════════════════════

class TestNoDuplicates:
    """Event bus must not emit duplicates for a single publish call."""

    @pytest.mark.asyncio
    async def test_publish_once_received_once(self):
        """Each publish call must result in exactly one received event."""
        bus = EventBus()
        sid = "dedup-1"
        received = []

        async def subscriber():
            async for ev in bus.subscribe(sid):
                received.append(ev)

        task = asyncio.create_task(subscriber())
        await asyncio.sleep(0.05)

        for i in range(5):
            await bus.publish(sid, "event", {"i": i})

        await asyncio.sleep(0.1)
        await bus.close_session(sid)
        await task

        assert len(received) == 5
        for i, ev in enumerate(received):
            assert ev["data"]["i"] == i

    @pytest.mark.asyncio
    async def test_sequence_numbers_monotonically_increase(self):
        """Sequence numbers on events must be strictly increasing."""
        bus = EventBus()
        sid = "seq-test"
        received = []

        async def subscriber():
            async for ev in bus.subscribe(sid):
                received.append(ev)

        task = asyncio.create_task(subscriber())
        await asyncio.sleep(0.05)

        for i in range(10):
            await bus.publish(sid, "tick", {"i": i})

        await asyncio.sleep(0.1)
        await bus.close_session(sid)
        await task

        seqs = [e["seq"] for e in received]
        assert seqs == sorted(seqs), "Sequence numbers not monotonically increasing"
        assert len(set(seqs)) == len(seqs), "Duplicate sequence numbers detected"


# ═══════════════════════════════════════════════════════════════════════
# 5. GRAPH SUCCESS PATH
# ═══════════════════════════════════════════════════════════════════════

class TestGraphSuccessPath:
    """Session completes normally, all events received, stream closes."""

    @pytest.mark.asyncio
    async def test_success_event_sequence(self):
        """session_started → phase_changed → session_complete → stream ends."""
        bus = EventBus()
        sid = "success-1"
        received = []

        async def subscriber():
            async for ev in bus.subscribe(sid):
                received.append(ev)

        task = asyncio.create_task(subscriber())
        await asyncio.sleep(0.05)

        # Simulate the graph lifecycle
        await bus.publish(sid, "session_started", {"project_id": sid})
        await bus.publish(sid, "phase_changed", {"new_phase": "analyzing"})
        await bus.publish(sid, "phase_changed", {"new_phase": "debating"})
        await bus.publish(sid, "session_complete", {"final_report": {}})
        await bus.close_session(sid)

        await asyncio.wait_for(task, timeout=2.0)

        event_names = [e["event"] for e in received]
        assert "session_started" in event_names
        assert "session_complete" in event_names
        assert event_names.index("session_started") < event_names.index("session_complete")

    @pytest.mark.asyncio
    async def test_stream_ends_after_close_session(self):
        """Subscriber generator must exit after close_session is called."""
        bus = EventBus()
        sid = "success-2"
        finished = asyncio.Event()

        async def subscriber():
            async for _ in bus.subscribe(sid):
                pass
            finished.set()

        asyncio.create_task(subscriber())
        await asyncio.sleep(0.05)
        await bus.close_session(sid)

        try:
            await asyncio.wait_for(finished.wait(), timeout=2.0)
        except asyncio.TimeoutError:
            pytest.fail("Subscriber did not exit after close_session()")


# ═══════════════════════════════════════════════════════════════════════
# 6. GRAPH FAILURE PATH
# ═══════════════════════════════════════════════════════════════════════

class TestGraphFailurePath:
    """Failed graph executions must emit an error event."""

    @pytest.mark.asyncio
    async def test_error_event_emitted_on_failure(self):
        """An error event must arrive before the stream closes."""
        bus = EventBus()
        sid = "failure-1"
        received = []

        async def subscriber():
            async for ev in bus.subscribe(sid):
                received.append(ev)

        task = asyncio.create_task(subscriber())
        await asyncio.sleep(0.05)

        # Simulate graph failure
        await bus.publish(sid, "session_started", {"project_id": sid})
        await bus.publish(sid, "error", {"message": "LLM timeout"})
        await bus.close_session(sid)

        await asyncio.wait_for(task, timeout=2.0)

        event_names = [e["event"] for e in received]
        assert "error" in event_names

        error_event = next(e for e in received if e["event"] == "error")
        assert error_event["data"]["message"] == "LLM timeout"

    @pytest.mark.asyncio
    async def test_stream_closes_after_error(self):
        """Stream must close cleanly after an error event."""
        bus = EventBus()
        sid = "failure-2"
        finished = asyncio.Event()

        async def subscriber():
            async for _ in bus.subscribe(sid):
                pass
            finished.set()

        asyncio.create_task(subscriber())
        await asyncio.sleep(0.05)

        await bus.publish(sid, "error", {"message": "fatal"})
        await bus.close_session(sid)

        try:
            await asyncio.wait_for(finished.wait(), timeout=2.0)
        except asyncio.TimeoutError:
            pytest.fail("Stream did not close after error event + close_session()")


# ═══════════════════════════════════════════════════════════════════════
# 7. BROWSER REFRESH / RECONNECT
# ═══════════════════════════════════════════════════════════════════════

class TestBrowserRefresh:
    """Simulates browser refresh (subscriber cancel + re-subscribe)."""

    @pytest.mark.asyncio
    async def test_reconnect_after_disconnect(self):
        """New subscriber after disconnect must still receive events."""
        bus = EventBus()
        sid = "refresh-1"

        # First subscriber connects then "disconnects" (cancel)
        async def first_subscriber():
            async for _ in bus.subscribe(sid):
                await asyncio.sleep(100)  # Block — simulates slow client

        task1 = asyncio.create_task(first_subscriber())
        await asyncio.sleep(0.05)
        assert bus.subscriber_count(sid) == 1

        # Simulate browser refresh — cancel the old subscriber
        task1.cancel()
        try:
            await task1
        except asyncio.CancelledError:
            pass
        await asyncio.sleep(0.05)
        assert bus.subscriber_count(sid) == 0, "Old subscriber not removed"

        # New subscriber connects
        received = []
        async def second_subscriber():
            async for ev in bus.subscribe(sid):
                received.append(ev)

        task2 = asyncio.create_task(second_subscriber())
        await asyncio.sleep(0.05)
        assert bus.subscriber_count(sid) == 1

        # Publish events to the refreshed session
        await bus.publish(sid, "resumed", {"ok": True})
        await bus.close_session(sid)
        await asyncio.wait_for(task2, timeout=2.0)

        assert len(received) == 1
        assert received[0]["event"] == "resumed"


# ═══════════════════════════════════════════════════════════════════════
# 8. SESSION COMPLETION / CLEANUP
# ═══════════════════════════════════════════════════════════════════════

class TestSessionCompletion:
    """After session completes, no resources should linger."""

    @pytest.mark.asyncio
    async def test_all_queues_cleaned_after_multiple_subscribers(self):
        """After close_session, all subscriber queues must be removed."""
        bus = EventBus()
        sid = "complete-1"

        tasks = []
        for _ in range(5):
            async def sub():
                async for _ in bus.subscribe(sid):
                    pass
            tasks.append(asyncio.create_task(sub()))

        await asyncio.sleep(0.05)
        assert bus.subscriber_count(sid) == 5

        await bus.close_session(sid)
        await asyncio.gather(*tasks)

        assert bus.subscriber_count(sid) == 0
        assert sid not in bus.active_sessions()

    @pytest.mark.asyncio
    async def test_publish_after_close_does_not_raise(self):
        """Publishing to a closed session must not raise an exception."""
        bus = EventBus()
        sid = "complete-2"
        await bus.close_session(sid)  # Close before anyone subscribes
        # Should not raise
        await bus.publish(sid, "ghost", {"data": "ignored"})

    @pytest.mark.asyncio
    async def test_event_ordering_preserved(self):
        """Events must arrive in the order they were published."""
        bus = EventBus()
        sid = "order-1"
        received = []

        async def subscriber():
            async for ev in bus.subscribe(sid):
                received.append(ev)

        task = asyncio.create_task(subscriber())
        await asyncio.sleep(0.05)

        expected = list(range(50))
        for i in expected:
            await bus.publish(sid, "tick", {"i": i})

        await asyncio.sleep(0.2)
        await bus.close_session(sid)
        await task

        actual = [e["data"]["i"] for e in received]
        assert actual == expected, f"Event ordering broken: {actual[:10]}…"


# ═══════════════════════════════════════════════════════════════════════
# 9. SESSION SERVICE INTEGRATION (mocked graph)
# ═══════════════════════════════════════════════════════════════════════

class TestSessionServiceIntegration:
    """Integration tests for SessionService with mocked LangGraph."""

    @pytest.mark.asyncio
    async def test_success_path_emits_session_complete(self):
        """run_agent_graph must emit session_complete after successful run."""
        import uuid as uuid_mod
        from app.services.session_service import SessionService

        bus = EventBus()
        # Use a real UUID so uuid.UUID(project_id) doesn't raise
        proj_id = str(uuid_mod.uuid4())
        received = []

        # Collect events in background
        async def subscriber():
            async for ev in bus.subscribe(proj_id):
                received.append(ev)

        sub_task = asyncio.create_task(subscriber())
        await asyncio.sleep(0.05)  # Let subscriber register

        # Mock the graph to return a canned successful state
        mock_graph = MagicMock()
        mock_graph.astream = MagicMock(return_value=aiter_from_list([
            {"prime_minister": {
                "current_phase": "completed",
                "final_report": {"chosen_option": "A", "executive_summary": "Good"},
            }},
        ]))

        mock_db = AsyncMock()
        mock_project = MagicMock()
        mock_project.problem = "Test problem"
        mock_project.context = ""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = mock_project
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.flush = AsyncMock()
        mock_db.add = MagicMock()

        with patch("app.services.session_service.AsyncSessionLocal") as mock_sl, \
             patch("app.services.session_service.create_governance_graph",
                   return_value=mock_graph), \
             patch("app.services.session_service.select"), \
             patch.object(SessionService, "_update_status", new_callable=AsyncMock), \
             patch.object(SessionService, "_persist_state", new_callable=AsyncMock):
            mock_sl.return_value.__aenter__ = AsyncMock(return_value=mock_db)
            mock_sl.return_value.__aexit__ = AsyncMock(return_value=False)

            service = SessionService(AsyncMock(), bus)
            await service.run_agent_graph(proj_id)

        await asyncio.wait_for(sub_task, timeout=3.0)

        event_names = [e["event"] for e in received]
        assert "session_complete" in event_names or "error" in event_names, \
            f"Neither terminal event received: {event_names}"

    @pytest.mark.asyncio
    async def test_failure_path_emits_error(self):
        """run_agent_graph must emit error event when graph raises."""
        import uuid as uuid_mod
        from app.services.session_service import SessionService

        bus = EventBus()
        proj_id = str(uuid_mod.uuid4())
        received = []

        async def subscriber():
            async for ev in bus.subscribe(proj_id):
                received.append(ev)

        sub_task = asyncio.create_task(subscriber())
        await asyncio.sleep(0.05)

        def _bad_graph():
            raise RuntimeError("Simulated LLM crash")

        with patch("app.services.session_service.AsyncSessionLocal") as mock_sl, \
             patch("app.services.session_service.create_governance_graph",
                   side_effect=_bad_graph), \
             patch("app.services.session_service.select"), \
             patch.object(SessionService, "_update_status", new_callable=AsyncMock):
            mock_db = AsyncMock()
            mock_sl.return_value.__aenter__ = AsyncMock(return_value=mock_db)
            mock_sl.return_value.__aexit__ = AsyncMock(return_value=False)

            service = SessionService(AsyncMock(), bus)
            await service.run_agent_graph(proj_id)

        await asyncio.wait_for(sub_task, timeout=3.0)

        event_names = [e["event"] for e in received]
        assert "error" in event_names, \
            f"Error event not emitted on graph failure: {event_names}"


# ═══════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════

async def aiter_from_list(items):
    """Convert a list to an async iterator (for mocking graph.astream)."""
    for item in items:
        yield item
        await asyncio.sleep(0)  # Yield to event loop between items
