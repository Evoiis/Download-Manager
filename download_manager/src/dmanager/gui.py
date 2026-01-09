from typing import Dict

from src.dmanager.asyncio_thread import AsyncioEventLoopThread
from src.dmanager.core import DownloadManager, DownloadEvent, DownloadState, DownloadMetadata

import tkinter as tk
from tkinter import ttk


class DownloadManagerGUI:

    def __init__(self, dmanager: DownloadManager, runner: AsyncioEventLoopThread, event_poll_rate: int=50):
        self.runner = runner
        self.dmanager = dmanager
        self.event_poll_rate = event_poll_rate
        
        self.url_input_element = None
        self.file_name_input_element = None
        self.table = None
        self.root = tk.Tk()
        self.download_data: Dict[int: DownloadMetadata] = dict()

        self._generate_gui_base_elements()
        self.root.protocol("WM_DELETE_WINDOW", self._shutdown)

        self.root.after(self.event_poll_rate, self._add_read_event_loop_to_async_thread)
    
    def run_gui_loop(self):
        self.root.mainloop()

    def _shutdown(self):
        self.root.destroy()

    def _add_read_event_loop_to_async_thread(self):
        self.runner.submit(self._read_event_loop())

    async def _read_event_loop(self):

        event = await self.dmanager.get_oldest_event()

        if event is not None:
            print(f"{event=}")
            # self.table.insert(
            #     "",
            #     tk.END,
            #     values=(1, "RUNNING", "http://example.com", "urmom.bin", "90%", "5 MB/s", None)
            # )

            pass

        self.root.after(self.event_poll_rate, self._add_read_event_loop_to_async_thread)

    def _add_new_download(self):
        url = self.url_input_element.get()
        file_name = self.file_name_input_element.get()

        if not url:
            return

        task_id = self.dmanager.add_download(
            url,
            file_name            
        )
        self.runner.submit(
            self.dmanager.start_download(
                task_id
            )
        )

    def _generate_gui_base_elements(self):
        tk.Label(self.root, text="Download URL:").grid(row=0, column=0, padx=5, pady=5)
        self.url_input_element = tk.Entry(self.root)
        self.url_input_element.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Output File Name(Optional):").grid(row=0, column=2, padx=5, pady=5)
        self.file_name_input_element = tk.Entry(self.root)
        self.file_name_input_element.grid(row=0, column=3, padx=5, pady=5)

        tk.Button(
            self.root, 
            text="Add Download", 
            command=self._add_new_download
        ).grid(row=0, column=4)

        table_columns = ("TaskID", "DownloadState", "URL", "OutputFile", "PercentComplete", "CurrentDownloadSpeed", "Error")
        self.table = ttk.Treeview(
            self.root,
            columns=table_columns,
            show="headings"
        )
        self.table.grid(row=2, column=0, columnspan=10)

        for column in table_columns:
            self.table.heading(column, text=column)
            self.table.column(column, width=100)

