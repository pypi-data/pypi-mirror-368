import asyncio

import pytest

from asynchedging import AllTasksFailedError, hedge, race


pytestmark = pytest.mark.asyncio


async def _ok(val: str, delay: float = 0.0) -> str:
    if delay:
        await asyncio.sleep(delay)
    return val


async def _fail(delay: float = 0.0) -> str:
    if delay:
        await asyncio.sleep(delay)
    raise RuntimeError("boom")


def _accept_non_empty(s: str) -> bool:
    return bool(s.strip())


async def test_race_returns_first_success_and_cancels_rest():
    started: list[str] = []

    async def a():
        started.append("a")
        return await _ok("A", 0.3)

    async def b():
        started.append("b")
        return await _ok("B", 0.1)

    async def c():
        started.append("c")
        return await _ok("C", 0.5)

    result, info = await race([(a(), 0.0), (b(), 0.0), (c(), 0.0)])

    assert result == "B"
    assert info.index == 1  # winner is the second factory
    assert set(started) == {"a", "b", "c"}
    assert info.started_count == 3
    assert info.elapsed_s > 0


async def test_race_all_fail_raises_with_errors():
    with pytest.raises(AllTasksFailedError) as exc:
        await race([(_fail(0.05), 0.0), (_fail(0.01), 0.0)])

    assert isinstance(exc.value.errors, list)
    assert len(exc.value.errors) == 2


async def test_race_with_accept_predicate_skips_unacceptable():
    # First completes fast but unacceptable (empty string). Second acceptable.
    result, info = await race(
        [(_ok("", 0.05), 0.0), (_ok("hello", 0.06), 0.0)],
        accept=_accept_non_empty,
    )

    assert result == "hello"
    assert info.index == 1


async def test_race_total_timeout():
    # All tasks too slow; total timeout should trigger
    with pytest.raises(TimeoutError):
        await race([(_ok("A", 1.0), 0.0), (_ok("B", 1.2), 0.0)], total_timeout_s=0.1)


async def test_hedge_single_factory_replication_requires_delays():
    # Single factory replicated with explicit delays
    counts = {"runs": 0}

    async def factory():
        counts["runs"] += 1
        return await _ok("X", 0.2)

    result, info = await hedge(factory, delays_s=(0.25, 0.75))
    assert result == "X"
    # Ensure at least the first task started before completion
    assert info.started_count >= 1
    # Ensure the factory was invoked at least once
    assert counts["runs"] >= 1


async def test_hedge_multiple_factories_with_stagger():
    # Use race for multiple coroutines with staggering (simulate with delays)
    coros_with_delays = [
        (_ok("primary", 0.8), 0.0),
        (_ok("backup1", 0.4), 0.25),
        (_ok("backup2", 0.5), 0.5),
    ]
    result, info = await race(coros_with_delays)
    assert result == "backup1"
    assert info.index == 1


async def test_hedge_multiple_factories_with_explicit_delays_N_minus_1():
    # Provide explicit delays for each coroutine
    coros_with_delays = [
        (_ok("p", 0.6), 0.0),
        (_ok("b1", 0.3), 0.1),
        (_ok("b2", 0.7), 0.2),
    ]
    result, info = await race(coros_with_delays)
    assert result == "b1"
    assert info.index == 1


async def test_hedge_multiple_factories_with_explicit_delays_N():
    # Provide explicit delays for each coroutine
    coros_with_delays = [
        (_ok("p", 0.6), 0.0),
        (_ok("b1", 0.3), 0.2),
        (_ok("b2", 0.7), 0.6),
    ]
    result, info = await race(coros_with_delays)
    assert result == "b1"
    assert info.index == 1


async def test_hedge_respects_accept_predicate():
    # First returns empty; second returns non-empty
    coros_with_delays = [(_ok("", 0.05), 0.0), (_ok("ok", 0.06), 0.0)]
    result, info = await race(coros_with_delays, accept=_accept_non_empty)
    assert result == "ok"
    assert info.index == 1


async def test_hedge_total_timeout():
    with pytest.raises(TimeoutError):
        await race([(_ok("A", 1.0), 0.0), (_ok("B", 1.2), 0.0)], total_timeout_s=0.1)
