import unittest

from jarvis_assistant.application.task_scheduling import TaskSchedulingService


class FakeScheduler:
    def __init__(self):
        self.scheduled = []

    def schedule(self, delay_ms, task):
        self.scheduled.append((delay_ms, task))
        return task


class TaskSchedulingServiceTests(unittest.TestCase):
    def test_converts_seconds_to_milliseconds(self):
        scheduler = FakeScheduler()
        service = TaskSchedulingService(scheduler)
        ran = []

        delay_ms = service.schedule_after(2.5, lambda: ran.append(True))

        self.assertEqual(delay_ms, 2500)
        self.assertEqual(scheduler.scheduled[0][0], 2500)
        scheduler.scheduled[0][1]()
        self.assertEqual(ran, [True])

    def test_clamps_negative_delay_to_zero(self):
        scheduler = FakeScheduler()
        service = TaskSchedulingService(scheduler)

        service.schedule_after(-10, lambda: None)

        self.assertEqual(scheduler.scheduled[0][0], 0)


if __name__ == "__main__":
    unittest.main()
