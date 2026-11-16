"""Headless delayed-task scheduling use case."""

from collections.abc import Callable

from ..domain.ports import TaskSchedulerPort


class TaskSchedulingService:
    def __init__(self, scheduler: TaskSchedulerPort) -> None:
        self._scheduler = scheduler

    def schedule_after(self, delay_seconds: int | float, task: Callable[[], None]) -> int:
        delay_ms = max(0, int(delay_seconds * 1000))
        self._scheduler.schedule(delay_ms, task)
        return delay_ms
