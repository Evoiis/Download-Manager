import asyncio
import pytest
import os
import logging


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
            await asyncio.sleep(0.5)
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
    chunks = [b"abc", b"def", b"ghi"]
    mock_url = "https://example.com/file.bin"
    mock_file_name = "file.bin"
    mock_resp = MockResponse(
        chunks=chunks, 
        status=206, 
        headers={
            "Content-Length": str(sum(len(c) for c in chunks)),
            "Accept-Ranges": "bytes"
        })
    mock_session = MockSession({mock_url: mock_resp})

    # Patch aiohttp.ClientSession() to return our mock session
    monkeypatch.setattr("aiohttp.ClientSession", lambda: mock_session)

    logging.debug("Add download to dmanager")
    dm = DownloadManager()
    future = async_thread_runner.submit(dm.add_and_start_download(mock_url, mock_file_name))

    task_id = future.result(1)
    logging.debug(f"{task_id=}")

    received_running_event = False

    logging.debug("Consume Events")
    counter = 0
    while True:
        await asyncio.sleep(1)
        counter += 1
        event = await dm.get_latest_event()
        logging.debug(f"{event=}")

        if event is None:
            continue

        if event.state == DownloadState.RUNNING and event.task_id == task_id:
            received_running_event = True
        
        if event.state == DownloadState.COMPLETED and event.task_id == task_id:
            assert(received_running_event, "Expected to receive download running event before completed event")
            break

        assert(counter < 20, "Download Manager took too long to respond!")
    
    download_metadata = dm.get_downloads()[1]

    logging.debug(download_metadata)

    assert(download_metadata.url == mock_url)
    assert(download_metadata.output_file == mock_file_name)
    assert(download_metadata.file_size_bytes == 9)
    assert(download_metadata.downloaded_bytes == 9)

    expected_text = "abcdefghi"
    with open(mock_file_name) as f:
        file_text = f.read()
        assert(file_text == expected_text, f"Downloaded file text did not match expected.\nDownloaded: {file_text}\nExpected: {expected_text}")

    if os.path.exists(mock_file_name):
        os.remove(mock_file_name)

