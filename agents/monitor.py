import watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import requests
import os

class MonitorHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print(f"File modified: {event.src_path}")
        if not os.path.isfile(event.src_path):
            return

        with open(event.src_path, "rb") as file:
            try:
                file.seek(-2, os.SEEK_END)
                while file.read(1) != b'\n':
                    file.seek(-2, os.SEEK_CUR)
            except OSError:
                file.seek(0)
            last_line = file.readline().decode()

        requests.post('http://localhost:8000/notify_file', json = {"file_name": event.src_path, "new_info": last_line})

    def on_created(self, event):
        print(f"File created: {event.src_path}")

    def on_deleted(self, event):
        print(f"File deleted: {event.src_path}")
    
    def on_moved(self, event):
        print(f"File moved from {event.src_path} to {event.dest_path}")
    
def start_monitoring(path):
    event_handler = MonitorHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print(f"Started monitoring {path}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
