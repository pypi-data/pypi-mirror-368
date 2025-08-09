import os
import time
from slips.log_watcher import LogWatcher  # adjust to your filename/module

def handle_log_line(line: str):
    print(f"[LOG] {line}")

log_path = os.path.expanduser("~/output/slips.log")

watcher = LogWatcher(
    log_file_path=log_path,
    on_new_line=handle_log_line,
    start_from_end=True  # Start tailing from the end like `tail -f`
)

if __name__ == "__main__":
    try:
        watcher.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
