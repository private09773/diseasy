"""Background loops: .task[seconds=/minutes=/hours=], .task_before_loop(),
.task_after_loop(), .task_start(), .task_stop()"""
import asyncio


class Loop:
    def __init__(self, callback, *, seconds: float = 0, minutes: float = 0, hours: float = 0):
        self.callback = callback
        self.interval = seconds + minutes * 60 + hours * 3600
        if self.interval <= 0:
            raise ValueError("Loop interval must be greater than zero.")
        self._before_loop = None
        self._after_loop = None
        self._task: asyncio.Task | None = None
        self._stopping = False

    def task_before_loop(self, func):
        self._before_loop = func
        return func

    def task_after_loop(self, func):
        self._after_loop = func
        return func

    async def _runner(self, *args, **kwargs):
        if self._before_loop:
            await self._before_loop()
        while not self._stopping:
            await self.callback(*args, **kwargs)
            await asyncio.sleep(self.interval)
        if self._after_loop:
            await self._after_loop()

    def task_start(self, *args, **kwargs) -> asyncio.Task:
        self._stopping = False
        self._task = asyncio.create_task(self._runner(*args, **kwargs))
        return self._task

    def task_stop(self):
        self._stopping = True


def task(seconds: float = 0, minutes: float = 0, hours: float = 0):
    """Decorator: @task(minutes=5) turns an async function into a Loop."""
    def decorator(func) -> Loop:
        return Loop(func, seconds=seconds, minutes=minutes, hours=hours)
    return decorator
