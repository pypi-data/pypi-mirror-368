from abc import abstractmethod
from enum import Enum, auto
from time import time, sleep
from typing import Callable
from tqdm import tqdm
from pulsebus import (
    EventSystem,
    BaseConsumer,
    BaseProducer,
    MessageTemplate,
    MessageBuilder,
    MessagePool
)

from utils.logger import logger


class DownloadingState(Enum):
    """
    Enum to define the different states of video downloading.
    """
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    PAUSED = auto()
    QUEUED = auto()

class DownloadMonitor:
    """Class responsible for client custom monitor strategy set up.
    
    - Abstract methods:
        - monitor_download_data: Expects download_data (download progress container)
          (Shall be overriten to have a successful monitoring and data printing)
    """
    @abstractmethod
    def monitor_download_data(self, download_data: dict) -> None:
        """
        Handle a download status update.

        This method must be overridden in subclasses. It will be called
        automatically by the downloader during the download process
        whenever there is a progress or status update.

        Parameters:
            status (dict): A dictionary containing download status data.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
        raise NotImplementedError("You must override monitor_download_data() to handle download updates.")


class ProgressDataStore:
    """A centralized data store for download tasks progress tracking."""
    _data = {}
    _reported = set()  # Track which tasks have sent their final message
    _expected = set()  # Track expected download tasks

    @classmethod
    def update(cls, key, value):
        cls._data[key] = value

    @classmethod
    def remove(cls, key):
        if key in cls._data:
            del cls._data[key]

    @classmethod
    def get(cls, key):
        return cls._data.get(key)

    @classmethod
    def all(cls):
        return cls._data.copy()

    @classmethod
    def set_expected(cls, download_ids):
        cls._expected = set(download_ids)
        
    @classmethod
    def mark_reported(cls, key):
        cls._reported.add(key)

    @classmethod
    def is_reported(cls, key):
        return key in cls._reported
    
    @classmethod
    def all_reported(cls):
        return not cls._data and cls._reported

# Define Producer and Consumer class
class DownloadTaskDataEnqeuer(BaseProducer):
    
    def __init__(self):
        super().__init__()

    def on_start(self):
        logger.info("Download Progress Tracker [PRG Msg Producer] Started!")
    
    def on_stop(self):
        logger.info("Download Progress Tracker [PRG Msg Producer] Stopped!")

    def produce(self):
        """Called by PulseBus when ready for new messages"""
        messages = []

        for download_task in list(ProgressDataStore._data.keys()):
            d = ProgressDataStore.get(download_task)
            if not d:
                continue

            # Create and fill the message
            message = download_tasks_data_pool.acquire()
            url = d.get("info_dict", {}).get("webpage_url") or d.get("url", "unknown")
            file_name = d.get("filename", "unknown")
            downloaded_bytes = d.get("downloaded_bytes", 0)
            total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            progress = float(f"{(downloaded_bytes / total_bytes) * 100:.2f}") if total_bytes else "N/A"
            raw_speed = d.get("speed")
            speed = f"{raw_speed / 1024:.2f} KB/s" if raw_speed else "N/A"
            eta = f"{d.get("eta", 0)}s" if d.get("eta") else "N/A"
            status = DownloadingState.IN_PROGRESS if d["status"] == "downloading" else DownloadingState.COMPLETED

            message.set_property("url", url)
            message.set_property("file_name", file_name)
            message.set_property("progress", progress)
            message.set_property("downloaded_bytes", downloaded_bytes)
            message.set_property("file_size", total_bytes)
            message.set_property("download_speed", speed)
            message.set_property("ETA", eta)
            message.set_property("status", status)
            message.set_property("timestamp", time())

            messages.append(message)

            # If finished and already reported, skip
            if d.get("status") == "finished":
                ProgressDataStore.mark_reported(download_task)
                ProgressDataStore.remove(download_task)  # Clear the data for this task
                continue

        # Stop producing if download tasks are completed
        if ProgressDataStore.all_reported():
            return None
        
        return messages  # Push message in pulsebus queue         


class DownloadTaskDataConsumer(BaseConsumer):
    def __init__(self, printer_fn: Callable):
        self.printer_fn = printer_fn

    def on_start(self):
        logger.info("Download Progress Tracker [PRG Msg Consumer] Started!")
    
    def on_stop(self):
        logger.info("Download Progress Tracker [PRG Msg Consumer] Stopped!")

    def consume(self, message: list[MessageTemplate]):
        """
        Called by PulseBus when new messages are in queue.
        Prints the download progress data using the client-defined printer function.
        """
        if not message:
            return
        
        # Iterate through the messages and print the progress
        for download_task_progress_msg in message:
            self.printer_fn(download_task_progress_msg.to_dict())
            download_tasks_data_pool.release(download_task_progress_msg)  # Release the message back to the pool



bar = tqdm(total=100)
def progress_tracking_printer(media_status: dict):
    """
    Base download progress printer function
    for monitoring downloads.

    Built-upon tqdm progress bar.

    """
    try:
        progress_num = media_status.get("progress", 0)  # Use .get() with default value
        bar.n = progress_num
        bar.refresh()
    except Exception as e:
        print(f"Error updating progress: {e}")


def progress_hook(d: dict) -> None:
    """
    A progress hook function to be used with yt-dlp.
    
    This function is called by yt-dlp to report download progress.
    It updates the download tasks progress data and calls the 
    client-defined progress tracker.
    
    Parameters:
        d (dict): A dictionary containing download status data.
    """
    download_task_id = d.get("info_dict", {}).get("webpage_url") or d.get("filename", "unknown")
    ProgressDataStore.update(download_task_id, d)  # Stores latest data 


class DownloadProgressTracker:
    """A class to track download tasks status and progress."""

    def __init__(self, printer_fn=progress_tracking_printer):
        # Initialize the message template
        self.progress_msg_template = (
            MessageBuilder()
                .add_field("url", "")
                .add_field("file_name", "")
                .add_field("progress", 0.0)
                .add_field("downloaded_bytes", 0)
                .add_field("file_size", 0)
                .add_field("download_speed", "")
                .add_field("ETA", 0)
                .add_field("status", DownloadingState.IN_PROGRESS)
                .add_field("timestamp", time())
                .build()
        )

        # Initialize the message pool and queue
        global download_tasks_data_pool
        download_tasks_data_pool = MessagePool(template=self.progress_msg_template, max_size=10)

        # Initialize the event system
        self.download_tracking_event_system = EventSystem()

        # Register producer and consumer
        self.download_tracking_event_system.register_producer(
            producer=DownloadTaskDataEnqeuer(),
            name="DownloadTaskProgressData"
        )

        self.download_tracking_event_system.register_consumer(
            consumer=DownloadTaskDataConsumer(printer_fn),
            name="DownloadTaskDataConsumer"
        )

        self.download_tracking_event_system.enable_auto_shutdown(6)

        # Start the event system
        self.download_tracking_event_system.start_all()

    def shutdown(self):
        """Shuts down the download progress tracker."""
        self.download_tracking_event_system.stop_all()
        logger.info("Download Progress Tracker has been shut down.")

    def maintain_system(self):
        """Maintains the event system."""
        while True:
            sleep(2)  # Keep the system running