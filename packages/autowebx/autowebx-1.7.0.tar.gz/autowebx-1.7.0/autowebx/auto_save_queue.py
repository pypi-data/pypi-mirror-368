import queue
import threading
import time
import json
from abc import ABC
from collections import deque
from collections.abc import Iterable
from threading import Event


class AutoSaveQueue(queue.Queue, Iterable, ABC):
    def __init__(self, file_path, auto_save_interval=5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_path = file_path
        self.auto_save_interval = auto_save_interval
        self._stop_event = Event()
        self._start_auto_save()

    def _start_auto_save(self):
        """Start the auto-save thread that saves the queue to the file at regular intervals."""
        self.auto_save_thread = threading.Thread(target=self._auto_save)
        self.auto_save_thread.daemon = True
        self.auto_save_thread.start()

    def _auto_save(self):
        """Automatically save the queue to a file at regular intervals."""
        while not self._stop_event.is_set():
            self.save()
            time.sleep(self.auto_save_interval)

    def save(self):
        """Save the current state of the queue to a file."""
        with self.mutex:
            open(self.file_path, 'w').write('\n'.join(str(item) for item in self))

    def stop(self):
        """Stop the auto-save thread."""
        self._stop_event.set()
        self.auto_save_thread.join()

    def put(self, item, *args, **kwargs):
        """Override the put method to save after adding an item."""
        super().put(item, *args, **kwargs)
        self.save()

    def get(self, *args, **kwargs):
        """Override the get method to save after removing an item."""
        item = super().get(*args, **kwargs)
        self.save()
        return item

    def load(self):
        """Load the queue from a file."""
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                with self.mutex:
                    self.queue = deque(data)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # Ignore errors when the file doesn't exist or is empty

# Usage
auto_queue = AutoSaveQueue("queue_data.json", auto_save_interval=10)
auto_queue.put("task 1")
auto_queue.put("task 2")
