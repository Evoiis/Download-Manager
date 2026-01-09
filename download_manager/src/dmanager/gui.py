from src.dmanager.asyncio_thread import AsyncioEventLoopThread
from src.dmanager.core import DownloadManager, DownloadEvent, DownloadState

import tkinter as tk


class DownloadManagerGUI:

    def __init__(self, dmanager: DownloadManager, runner: AsyncioEventLoopThread):
        self.runner = runner
        self.dmanager = dmanager
        
        self.url_input = None
        self.file_name_input = None

        self.root = tk.Tk()
        self._generate_gui_base_elements()
        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)
        

    def shutdown(self):
        self.root.destroy()

    def add_new_download(self):
        url = self.url_input.get()
        file_name = self.file_name_input.get()

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
        # Input 1
        tk.Label(self.root, text="Download URL:").grid(row=0, column=0, padx=5, pady=5)
        self.url_input = tk.Entry(self.root)
        self.url_input.grid(row=0, column=1, padx=5, pady=5)

        # Input 2
        tk.Label(self.root, text="Output File Name(Optional):").grid(row=0, column=2, padx=5, pady=5)
        self.file_name_input = tk.Entry(self.root)
        self.file_name_input.grid(row=0, column=3, padx=5, pady=5)

        tk.Button(
            self.root, 
            text="Add Download", 
            command=self.add_new_download
        ).grid(row=0, column=4)

    def run_gui_loop(self):
        self.root.mainloop()
