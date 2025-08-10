from __future__ import annotations

"""
Custom helpers for task polling.

This module adds `Task.poll()` and `Task.apoll()` methods at runtime to the
generated `Task` model, without modifying generated code directly.

Usage:
    task = client.tasks.get(task_id)
    task = task.poll(client)  # blocks until terminal state

    # async
    task = await async_client.tasks.get(task_id)
    task = await task.apoll(async_client)
"""

import time
import asyncio
from typing import Protocol, cast

from .._types import NOT_GIVEN, NotGiven
from .._client import Chunkr, AsyncChunkr
from ..types.task import Task as _Task
from .._exceptions import ChunkrError

TERMINAL_STATUSES = {"Succeeded", "Failed", "Cancelled"}


def _task_poll(
    self: _Task,
    client: Chunkr,
    *,
    interval: float = 0.5,
    timeout: float = 600.0,
    include_chunks: bool | NotGiven = NOT_GIVEN,
    base64_urls: bool | NotGiven = NOT_GIVEN,
) -> _Task:
    """Poll the task until it reaches a terminal status.

    Args:
        client: Synchronous Chunkr client instance.
        interval: Seconds to sleep between polls.
        timeout: Maximum total seconds to wait before raising an error.
        include_chunks: Whether to include chunks in the output response for each poll.
        base64_urls: Whether to return base64 encoded URLs.
    """
    start_time = time.monotonic()
    current: _Task = self

    class _TasksGetProtocol(Protocol):
        def get(
            self,
            task_id: str,
            *,
            base64_urls: bool | NotGiven = NOT_GIVEN,
            include_chunks: bool | NotGiven = NOT_GIVEN,
        ) -> _Task: ...

    resource = cast(_TasksGetProtocol, client.tasks)

    while current.status not in TERMINAL_STATUSES:
        if time.monotonic() - start_time > timeout:
            raise ChunkrError("Task polling timed out.")

        if interval > 0:
            time.sleep(interval)

        current = resource.get(
            current.task_id,
            include_chunks=include_chunks,
            base64_urls=base64_urls,
        )

    return current


async def _task_apoll(
    self: _Task,
    client: AsyncChunkr,
    *,
    interval: float = 0.5,
    timeout: float = 600.0,
    include_chunks: bool | NotGiven = NOT_GIVEN,
    base64_urls: bool | NotGiven = NOT_GIVEN,
) -> _Task:
    """Async poll the task until it reaches a terminal status."""
    start_time = time.monotonic()
    current: _Task = self

    class _AsyncTasksGetProtocol(Protocol):
        async def get(
            self,
            task_id: str,
            *,
            base64_urls: bool | NotGiven = NOT_GIVEN,
            include_chunks: bool | NotGiven = NOT_GIVEN,
        ) -> _Task: ...

    aresource = cast(_AsyncTasksGetProtocol, client.tasks)

    while current.status not in TERMINAL_STATUSES:
        if time.monotonic() - start_time > timeout:
            raise ChunkrError("Task polling timed out.")

        if interval > 0:
            await asyncio.sleep(interval)

        current = await aresource.get(
            current.task_id,
            include_chunks=include_chunks,
            base64_urls=base64_urls,
        )

    return current


# Attach methods to the generated Task model
_Task.poll = _task_poll  # type: ignore[attr-defined]
_Task.apoll = _task_apoll  # type: ignore[attr-defined]


