import asyncio
import pytest

from dmanager.asyncio_thread import AsyncioEventLoopThread


@pytest.fixture
def async_thread_runner():
    runner = AsyncioEventLoopThread()
    yield runner
    runner.shutdown()
