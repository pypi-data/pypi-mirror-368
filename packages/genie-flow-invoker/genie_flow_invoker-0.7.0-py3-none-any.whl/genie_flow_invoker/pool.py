from queue import Queue
from typing import Optional

from genie_flow_invoker import GenieInvoker


class InvokersPool:
    """
    A simple context manager that gets invokers from a queue and returns them when the
    context is closed. Makes the queue serve as a pool of invokers.
    """

    def __init__(self, queue: Queue[GenieInvoker]):
        self._queue = queue
        self._current_invoker: Optional[GenieInvoker] = None

    def __enter__(self):
        if self._current_invoker is None:
            self._current_invoker = self._queue.get()
        return self._current_invoker

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self._current_invoker is not None:
            self._queue.put(self._current_invoker)
            self._current_invoker = None
