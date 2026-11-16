from collections.abc import Callable

from PyQt6.QtCore import QTimer

from ..domain.ports import TaskSchedulerPort


class QtTaskScheduler(TaskSchedulerPort):
    """Qt-backed scheduler that retains active timers until completion."""

    def __init__(self, owner) -> None:
        self._owner = owner
        self._active_timers = []

    def schedule(self, delay_ms: int, task: Callable[[], None]) -> QTimer:
        timer = QTimer(self._owner)
        timer.setSingleShot(True)

        def run_and_release() -> None:
            try:
                task()
            finally:
                if timer in self._active_timers:
                    self._active_timers.remove(timer)
                timer.deleteLater()

        timer.timeout.connect(run_and_release)
        timer.start(delay_ms)
        self._active_timers.append(timer)
        return timer
