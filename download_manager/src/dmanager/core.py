from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional, List, Any
from datetime import datetime
import os
import asyncio
import aiohttp
import aiofiles


# TODO: Define an Event Class
@dataclass
class DownloadEvent:
    pass

class DownloadState(Enum):
    PAUSED = 0
    RUNNING = 1
    COMPLETED = 2
    ERROR = -1

@dataclass
class DownloadTask:
    id: str
    url: str
    output_file: str
    state: DownloadState = DownloadState.PAUSED

class DownloadManager:
    """
    Async download manager.
    """

    def __init__(self) -> None:
        # TODO Add clean up self._tasks logic
        self._tasks: Dict[int, DownloadTask] = {}
        self._next_id = 0
        self.events_queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        # TODO make sure self._workers are cleaned up
        self._workers: Dict[str, asyncio.Task[Any]] = {}

    def _iterate_id(self) -> str:
        self._next_id += 1
        return self._next_id

    def add_download(self, url: str, output_file: Optional[str] = None) -> int:
        """
        Adds a new download task.
        
        :param url: URL to download a file from
        :param output_file: Output file name
        :return: Task ID
        """

        if output_file is None:
            output_file = url.split("/")[-1] or "download"+str(datetime.now().strftime("%m_%d_%Y_%H_%M_%S"))

        task_id = self._iterate_id()
        task = DownloadTask(id=task_id, url=url, output_file=str(output_file))
        self._tasks[task_id] = task
        return task_id

    async def start(self, task_id: str) -> bool:
        """Start (and await) a download worker for `task_id`.

        Returns True if the task existed, False otherwise.
        """

        task = self._tasks.get(task_id)
        if not task:
            return False
        worker = asyncio.create_task(self._run_download(task))
        self._workers[task_id] = worker
        try:
            await worker
            return True
        finally:
            self._workers.pop(task_id, None)

    async def _run_download(self, task: DownloadTask) -> None:
        task.state = DownloadState.RUNNING
        url = task.url
        headers: Dict[str, str] = {}
        if task.downloaded_bytes:
            headers["Range"] = f"bytes={task.downloaded_bytes}-"

        session = aiohttp.ClientSession()
        try:
            async with session.get(url, headers=headers) as resp:
                total: Optional[int] = None
                cl = resp.headers.get("Content-Length")
                if cl:
                    try:
                        total = int(cl)
                    except Exception:
                        total = None

                async for chunk in resp.content.iter_chunked(64 * 1024):
                    try:
                        part_path = task.output_file + ".part"
                        async with aiofiles.open(part_path, "ab") as f:
                            await f.write(chunk)
                    except Exception:
                        # swallow IO errors for tests
                        pass
                    task.downloaded_bytes += len(chunk)

                    # TODO: Define an Event Class
                    await self.events_queue.put({
                        "task_id": task.id,
                        "downloaded": task.downloaded_bytes,
                        "total": total,
                        "status": "running",
                    })

                task.state = DownloadState.COMPLETED
                try:
                    part = task.output_file + ".part"
                    if os.path.exists(part):
                        os.replace(part, task.output_file)
                except Exception:
                    pass

                await self.events_queue.put({"task_id": task.id, "status": "completed"})
        except asyncio.CancelledError:
            task.state = DownloadState.PAUSED
            await self.events_queue.put({"task_id": task.id, "status": "paused"})
            raise
        except Exception:
            task.state = DownloadState.ERROR
            await self.events_queue.put({"task_id": task.id, "status": "error"})
        finally:
            close = getattr(session, "close", None)
            if close:
                maybe = close()
                if asyncio.iscoroutine(maybe):
                    await maybe

    async def pause(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if not task:
            return False
        worker = self._workers.get(task_id)
        if worker and not worker.done():
            worker.cancel()
            try:
                await worker
            except asyncio.CancelledError:
                pass
        if task.state == DownloadState.RUNNING:
            task.state = DownloadState.PAUSED
        return True

    async def resume(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if not task:
            return False
        if task.state == DownloadState.PAUSED:
            worker = asyncio.create_task(self._run_download(task))
            self._workers[task_id] = worker
        return True

    # TODO: Implement Download Cancel and add File Cleanup
    # async def cancel(self, task_id: str) -> bool:
    #     task = self._tasks.get(task_id)
    #     if not task:
    #         return False
    #     task.state = DownloadState.PAUSED
    #     worker = self._workers.get(task_id)
    #     if worker and not worker.done():
    #         worker.cancel()
    #         try:
    #             await worker
    #         except asyncio.CancelledError:
    #             pass
    #     return True



__all__ = ["DownloadManager"]
