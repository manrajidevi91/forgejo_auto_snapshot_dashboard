
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utils.logger import app_logger as logger

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        # Debounce the callback to avoid firing too often
        self.debounced_callback = debounce(wait=5)(self.callback)

    def on_any_event(self, event):
        # We don't care about directory events
        if event.is_directory:
            return
        logger.debug(f"File system event: {event.event_type} on {event.src_path}")
        self.debounced_callback(event.src_path)

def watch_project(path, callback):
    """Watches a project folder for changes."""
    event_handler = ChangeHandler(callback)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    logger.info(f"Started watching project at {path}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
