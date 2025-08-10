from __future__ import annotations

from typing import Any, List, cast
from datetime import datetime, timezone

from chunkr_ai import Chunkr, AsyncChunkr
from chunkr_ai.types.task import Task


def _mk_task(status: str) -> Task:
    return Task.construct(
        configuration={
            "chunk_processing": {},
            "error_handling": "Fail",
            "llm_processing": {},
            "ocr_strategy": "All",
            "segment_processing": {},
            "segmentation_strategy": "Page",
        },
        created_at=datetime.now(timezone.utc),
        message="",
        status=status,
        task_id="task_123",
    )


class _TasksStub:
    def __init__(self, responses: List[Task]) -> None:
        self._responses = responses

    def get(self, task_id: str, *, base64_urls: Any = None, include_chunks: Any = None) -> Task:  # noqa: ARG002
        return self._responses.pop(0)


class _AsyncTasksStub:
    def __init__(self, responses: List[Task]) -> None:
        self._responses = responses

    async def get(self, task_id: str, *, base64_urls: Any = None, include_chunks: Any = None) -> Task:  # noqa: ARG002
        return self._responses.pop(0)


def test_poll_reaches_terminal_state() -> None:
    client = Chunkr(base_url="http://127.0.0.1:4010", api_key="key", _strict_response_validation=True)

    initial = _mk_task("Starting")
    client.tasks = _TasksStub([_mk_task("Processing"), _mk_task("Succeeded")])  # type: ignore[assignment]

    # avoid static type errors for monkey-patched method
    final = cast(Any, initial).poll(client, interval=0.0, timeout=2.0)
    assert final.status == "Succeeded"

async def test_apoll_reaches_terminal_state() -> None:
    client = AsyncChunkr(base_url="http://127.0.0.1:4010", api_key="key", _strict_response_validation=True)

    initial = _mk_task("Starting")
    client.tasks = _AsyncTasksStub([_mk_task("Processing"), _mk_task("Succeeded")])  # type: ignore[assignment]

    final = await cast(Any, initial).apoll(client, interval=0.0, timeout=2.0)
    assert final.status == "Succeeded"


