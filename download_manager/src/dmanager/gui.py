from src.dmanager.asyncio_thread import AsyncioEventLoopThread
from src.dmanager.core import DownloadManager, DownloadEvent, DownloadState

import tkinter as tk


class DownloadManagerGUI:

    def __init__(self, dmanager: DownloadManager, runner: AsyncioEventLoopThread):
        self.runner = runner
        self.dmanager = dmanager
        
        self.root = tk.Tk()
        self._generate_gui_elements()
        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)

    def shutdown(self):
        self.root.destroy()

    def test_async(self):
        task_id = self.dmanager.add_download(
            "https://example.com/",
            "test.txt"
        )
        self.runner.submit(
            self.dmanager.start_download(
                task_id
            )
        )

    def _generate_gui_elements(self):
        tk.Button(
            self.root, 
            text="Test Button", 
            command=self.test_async
        ).pack()

    def run_gui_loop(self):
        self.root.mainloop()

