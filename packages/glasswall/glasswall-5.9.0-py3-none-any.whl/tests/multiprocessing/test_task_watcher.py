

import time
import unittest
from multiprocessing import Queue

from glasswall.multiprocessing.task_watcher import TaskWatcher
from glasswall.multiprocessing.tasks import Task, TaskResult


def sample_task() -> str:
    return "Task completed!"


def long_running_task() -> None:
    time.sleep(1)
    return "Task completed!"


def exception_task() -> None:
    raise ValueError("Test exception")


def memory_task() -> bytes:
    allocated_memory = bytearray(100 * 1024 * 1024)  # 100 MiB
    time.sleep(1)
    return allocated_memory


class TestTaskWatcher(unittest.TestCase):
    def test_task_watcher_auto_start(self):
        # Test task watcher with auto_start=True
        task = Task(sample_task)
        queue: "Queue[TaskResult]" = Queue()
        TaskWatcher(task, queue)
        task_result = queue.get()
        self.assertTrue(task_result.success)
        self.assertEqual(task_result.result, "Task completed!")

    def test_task_watcher_manual_start(self):
        # Test task watcher with auto_start=False
        task = Task(sample_task)
        queue: "Queue[TaskResult]" = Queue()
        watcher = TaskWatcher(task, queue, auto_start=False)
        watcher.start_task()
        watcher.watch_task()
        watcher.update_queue()
        task_result = queue.get()
        self.assertTrue(task_result.success)
        self.assertEqual(task_result.result, "Task completed!")

    def test_task_watcher_timeout_failure(self):
        # Test task watcher with timeout
        task = Task(long_running_task)
        queue: "Queue[TaskResult]" = Queue()
        TaskWatcher(task, queue, timeout_seconds=0.1)  # 0.1s timeout for 1s task
        task_result = queue.get()
        self.assertFalse(task_result.success)
        self.assertIsNone(task_result.result)
        self.assertIsInstance(task_result.exception, TimeoutError)

        # Check attribute presence/absence based on initial setting of 'timeout_seconds'/'memory_limit_in_gib'
        self.assertTrue(hasattr(task_result, "timeout_seconds"))
        self.assertTrue(hasattr(task_result, "timed_out"))
        self.assertTrue(hasattr(task_result, "start_time"))
        self.assertTrue(hasattr(task_result, "end_time"))
        self.assertTrue(hasattr(task_result, "elapsed_time"))

        self.assertTrue(hasattr(task_result, "memory_limit_in_gib"))
        self.assertFalse(hasattr(task_result, "max_memory_used_in_gib"))
        self.assertFalse(hasattr(task_result, "out_of_memory"))

    def test_task_watcher_timeout_success(self):
        # Test task watcher with timeout
        task = Task(long_running_task)
        queue: "Queue[TaskResult]" = Queue()
        TaskWatcher(task, queue, timeout_seconds=5)  # 5s timeout for 1s task
        task_result = queue.get()
        self.assertTrue(task_result.success)
        self.assertEqual(task_result.result, "Task completed!")
        self.assertIsNone(task_result.exception)

        # Check attribute presence/absence based on initial setting of 'timeout_seconds'/'memory_limit_in_gib'
        self.assertTrue(hasattr(task_result, "timeout_seconds"))
        self.assertTrue(hasattr(task_result, "timed_out"))
        self.assertTrue(hasattr(task_result, "start_time"))
        self.assertTrue(hasattr(task_result, "end_time"))
        self.assertTrue(hasattr(task_result, "elapsed_time"))

        self.assertTrue(hasattr(task_result, "memory_limit_in_gib"))
        self.assertFalse(hasattr(task_result, "max_memory_used_in_gib"))
        self.assertFalse(hasattr(task_result, "out_of_memory"))

    def test_task_watcher_exception(self):
        # Test task watcher with task raising an exception
        task = Task(exception_task)
        queue: "Queue[TaskResult]" = Queue()
        TaskWatcher(task, queue)
        task_result = queue.get()
        self.assertFalse(task_result.success)
        self.assertIsInstance(task_result.exception, ValueError)
        self.assertIn("Test exception", str(task_result.exception))

    def test_task_watcher_memory_limit_success(self):
        # Test task watcher with memory limit
        task = Task(memory_task)
        queue: "Queue[TaskResult]" = Queue()
        TaskWatcher(task, queue, memory_limit_in_gib=1)  # 1 GiB limit with 100 MiB used
        task_result = queue.get()
        self.assertTrue(task_result.success)

        # Check attribute presence/absence based on initial setting of 'timeout_seconds'/'memory_limit_in_gib'
        self.assertTrue(hasattr(task_result, "timeout_seconds"))
        self.assertFalse(hasattr(task_result, "timed_out"))
        self.assertTrue(hasattr(task_result, "start_time"))
        self.assertTrue(hasattr(task_result, "end_time"))
        self.assertTrue(hasattr(task_result, "elapsed_time"))

        self.assertTrue(hasattr(task_result, "memory_limit_in_gib"))
        self.assertTrue(hasattr(task_result, "max_memory_used_in_gib"))
        self.assertTrue(hasattr(task_result, "out_of_memory"))

    def test_task_watcher_memory_limit_failure(self):
        # Test task watcher with memory limit
        task = Task(memory_task)
        queue: "Queue[TaskResult]" = Queue()
        TaskWatcher(task, queue, memory_limit_in_gib=0.05)  # 50 MiB limit with 100 MiB used
        task_result = queue.get()
        self.assertFalse(task_result.success)

        # Check attribute presence/absence based on initial setting of 'timed_out'/'memory_limit_in_gib'
        self.assertTrue(hasattr(task_result, "timeout_seconds"))
        self.assertFalse(hasattr(task_result, "timed_out"))
        self.assertTrue(hasattr(task_result, "start_time"))
        self.assertTrue(hasattr(task_result, "end_time"))
        self.assertTrue(hasattr(task_result, "elapsed_time"))

        self.assertTrue(hasattr(task_result, "memory_limit_in_gib"))
        self.assertTrue(hasattr(task_result, "max_memory_used_in_gib"))
        self.assertTrue(hasattr(task_result, "out_of_memory"))


if __name__ == "__main__":
    unittest.main()
