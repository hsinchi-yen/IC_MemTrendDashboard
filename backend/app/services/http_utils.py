import asyncio
from collections.abc import Awaitable, Callable


class QuotaExceededError(RuntimeError):
    pass


async def with_retries(
    func: Callable[[], Awaitable],
    retries: int = 3,
    base_delay: float = 1.0,
):
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            return await func()
        except QuotaExceededError:
            raise
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt == retries - 1:
                break
            await asyncio.sleep(base_delay * (2**attempt))
    if last_error:
        raise last_error
    raise RuntimeError("retry_failed")


class AsyncRateLimiter:
    def __init__(self, min_interval_seconds: float) -> None:
        self.min_interval_seconds = min_interval_seconds
        self._lock = asyncio.Lock()
        self._last_call = 0.0

    async def wait(self) -> None:
        async with self._lock:
            now = asyncio.get_running_loop().time()
            delta = now - self._last_call
            if delta < self.min_interval_seconds:
                await asyncio.sleep(self.min_interval_seconds - delta)
            self._last_call = asyncio.get_running_loop().time()
