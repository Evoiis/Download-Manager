import asyncio
import pytest

import logging

logger = logging.getLogger(__name__)

class MockResponse:
    def __init__(self, chunks, status=200, headers=None):
        self._chunks = chunks
        self.status = status
        self.headers = headers or {}
        self.content = self

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def iter_chunked(self, n):
        for c in self._chunks:
            await asyncio.sleep(0)  # allow scheduling
            yield c


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


@pytest.mark.asyncio
async def test_dm_add_and_start_download(monkeypatch, async_thread_runner):
    from dmanager.core import DownloadManager, DownloadState

    # Prepare mock session
    logger.debug("Prepare mock session")
    chunks = [b"abc", b"def", b"ghi"]
    mock_resp = MockResponse(chunks=chunks, status=200, headers={"Content-Length": str(sum(len(c) for c in chunks))})
    mock_session = MockSession({"https://example.com/file.bin": mock_resp})

    # Patch aiohttp.ClientSession() to return our mock session
    monkeypatch.setattr("aiohttp.ClientSession", lambda: mock_session)

    logger.debug("Add download to dmanager")
    dm = DownloadManager()
    # task_id = await dm.add_and_start_download("https://example.com/file.bin", "file.bin")
    future = async_thread_runner.submit(dm.add_and_start_download("https://example.com/file.bin", "file.bin"))

    # with pytest.raises(Exception):
    task_id = future.result(1)
    logger.debug(f"{task_id=}")

    received_running_event = False

    # Consume events
    logger.debug("Consume Events")
    counter = 0
    while True:
        await asyncio.sleep(1)
        counter += 1
        event = await dm.get_latest_event()
        logger.debug(f"{event=}")

        if event is None:
            continue

        if event.state == DownloadState.RUNNING and event.task_id == task_id:
            received_running_event = True
        
        if event.state == DownloadState.COMPLETED and event.task_id == task_id:
            assert(received_running_event, "Expected to receive download running event before completed event")
            break

        assert(counter < 20, "Download Manager took too long to respond!")

