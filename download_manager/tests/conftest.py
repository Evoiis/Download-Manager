import asyncio
import pytest
import os
import logging

from dmanager.asyncio_thread import AsyncioEventLoopThread


class MockResponse:
    def __init__(self, status, headers={}):
        self.status = status
        self.headers = headers
        self.content = self
        self.queue = asyncio.Queue()
        self.stop = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def iter_chunked(self, chunk_size_limit):
        while not self.stop or not self.queue.empty():
            if not self.queue.empty():
                chunk = await self.queue.get()
                yield chunk
            else:
                await asyncio.sleep(0.5)
    
    async def insert_chunk(self, chunk):
        await self.queue.put(chunk)

    def end_response(self):
        self.stop = True

    async def empty_queue(self):
        while not self.queue.empty():
            await self.queue.get()

class MockSession:
    def __init__(self, responses):
        self._responses = responses

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    def get(self, url, headers=None):
        return self._responses[url]

    def head(self, url):
        return self._responses[url]


@pytest.fixture
def async_thread_runner():
    runner = AsyncioEventLoopThread()
    yield runner
    runner.shutdown()

@pytest.fixture
def create_mock_response():
    def factory(status, headers=None):
        return MockResponse(status, headers)

    return factory

@pytest.fixture
def set_mock_session(monkeypatch):
    def factory(mock_url, mock_response):
        monkeypatch.setattr("aiohttp.ClientSession", lambda: MockSession({mock_url: mock_response}))
    
    return factory

@pytest.fixture
def create_mock_response_and_set_mock_session(monkeypatch):

    def factory(return_status, headers, mock_url):
        mock_res = MockResponse(return_status, headers)
        monkeypatch.setattr("aiohttp.ClientSession", lambda: MockSession({mock_url: mock_res}))
        return mock_res

    return factory

@pytest.fixture
def test_file_setup_and_cleanup(request):
    test_file_name = ""

    def setup(file_name):
        nonlocal test_file_name
        test_file_name = file_name
        if os.path.exists(test_file_name):
            os.remove(test_file_name)

    def cleanup():
        if os.path.exists(test_file_name):
            logging.debug(f"Cleaning up {test_file_name=}")
            os.remove(test_file_name)
    
    request.addfinalizer(cleanup)
    yield setup
