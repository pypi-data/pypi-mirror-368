import os
import time
import threading
from typing import Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class LogWatcher:
    """
    Real-time log file watcher for streaming new lines as they are written.
    """

    def __init__(self, log_file_path: str, on_new_line: Callable[[str], None], start_from_end: bool = True):
        self.log_file_path = os.path.abspath(log_file_path)
        self.on_new_line = on_new_line
        self.start_from_end = start_from_end
        self._file = None
        self._running = False
        self._observer: Optional[Observer] = None
        self._lock = threading.Lock()

    class _LogFileHandler(FileSystemEventHandler):
        def __init__(self, watcher):
            self.watcher = watcher

        def on_modified(self, event):
            if os.path.abspath(event.src_path) == self.watcher.log_file_path:
                with self.watcher._lock:
                    self.watcher._read_new_lines()

    def _read_new_lines(self):
        lines = self._file.readlines()
        for line in lines:
            self.on_new_line(line.strip())

    def start(self):
        if not os.path.isfile(self.log_file_path):
            raise FileNotFoundError(f"Log file not found: {self.log_file_path}")

        self._running = True
        self._file = open(self.log_file_path, "r", encoding="utf-8", buffering=1)
        if self.start_from_end:
            self._file.seek(0, os.SEEK_END)
        else:
            self._read_new_lines()

        event_handler = self._LogFileHandler(self)
        self._observer = Observer(timeout=0.1)
        directory = os.path.dirname(self.log_file_path)
        self._observer.schedule(event_handler, path=directory, recursive=False)
        self._observer.start()

        # print(f"[LogWatcher] Monitoring started: {self.log_file_path}")

    def stop(self):
        self._running = False
        if self._observer:
            self._observer.stop()
            self._observer.join()
        if self._file:
            self._file.close()
        # print("[LogWatcher] Stopped.")
