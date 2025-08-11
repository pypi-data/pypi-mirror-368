import time
import asyncio
import pytest
from twill_throttle import FuncPerMin, SharedRateLimiter

def test_funcpermin_limits_calls():
    call_counter = {"count": 0}

    @FuncPerMin(max_calls_per_minute=2)
    def inc_counter():
        call_counter["count"] += 1
        return call_counter["count"]

    # קריאות ראשונות עובדות מיד
    assert inc_counter() == 1
    assert inc_counter() == 2

    start = time.time()
    # הקריאה השלישית תחכה עד שיעבור הזמן (כמעט 60 שניות)
    inc_counter()
    elapsed = time.time() - start
    assert elapsed >= 58  # צריך להיות לפחות כמעט דקה, אפשר לתת מרווח קטן

def test_sharedratelimiter_sync():
    limiter = SharedRateLimiter(max_calls_per_minute=2)
    call_counter = {"count": 0}

    @limiter
    def inc_counter():
        call_counter["count"] += 1
        return call_counter["count"]

    assert inc_counter() == 1
    assert inc_counter() == 2

    start = time.time()
    inc_counter()
    elapsed = time.time() - start
    assert elapsed >= 58

@pytest.mark.asyncio
async def test_sharedratelimiter_async():
    limiter = SharedRateLimiter(max_calls_per_minute=2)
    call_counter = {"count": 0}

    @limiter
    async def inc_counter():
        call_counter["count"] += 1
        return call_counter["count"]

    assert await inc_counter() == 1
    assert await inc_counter() == 2

    start = time.time()
    await inc_counter()
    elapsed = time.time() - start
    assert elapsed >= 58
