"""Helpers for bridging async and sync code."""

from typing import Awaitable, Any
import asyncio


__all__ = ("async_to_sync",)


def async_to_sync(awaitable: Awaitable) -> Any:
    """Execute an awaitable in a new event loop and return its result."""

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(awaitable)
