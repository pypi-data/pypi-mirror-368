from pulsebus import EventSystem, MessageBuilder, MessagePool

from download_strategies.downloading_strategy import DownloadingStrategy
from .download_enqueuer import DownloadEnqueuer
from .download_worker import DownloadWorker

from core.media_object_class import MediaObject
from progress_tracking.progress_tracking import DownloadProgressTracker
from utils.media_files_bank import MediaFilesBank
from utils.logger import logger

from typing import Optional, Callable
from time import sleep

class DownloadManager:
    """
    Central orchestrator of the event-driven downloading system.

    The `DownloadManager` serves as the entry point and lifecycle controller
    for the entire download infrastructure. It is responsible for initializing,
    configuring, and managing the components that make up the download pipeline,
    including the task queue, download enqueuer, workers, and strategy resolution.

    It follows the Strategy design pattern to allow dynamic selection of
    download strategies (e.g., basic, parallel, audio-only), and the
    Producer–Consumer model to decouple task submission from task execution.

    Upon startup, the manager:
        - Initializes the shared download queue
        - Sets up and wires components (enqueuer, workers, object pool, tracker)
        - Assigns or resolves the appropriate download strategy
        - Starts worker threads or event loops as needed

    Upon shutdown, it:
        - Gracefully stops workers and consumers
        - Drains or closes the task queue
        - Cleans up resources and temporary state

    Responsibilities:
        - Control the system lifecycle (`start()`, `shutdown()`)
        - Provide a high-level `enqueue()` method to accept media files
        - Configure and inject the selected download strategy
        - Tie together all internal components (e.g., enqueuer, tracker, queue, pool)

    Typical usage:
        manager = DownloadManager(
                                   strategy=ParallelDownloadStrategy(),
                                   max_workers=2,
                                   download_queue_size=5,
                                   message_pool_size=3,
                                   progress_tracker_callback=DownloadMonitor.monitor_download_data
                                )
        manager.enqueue(media1)
        manager.enqueue(media2)
        ...
        manager.maintain_system()

    Attributes:
        queue: The shared task queue for media objects.
        strategy: The download strategy used by all workers.
        workers: List of DownloadWorker instances.
        enqueuer: The DownloadEnqueuer instance for media submissions.
        object_pool: An internal object pool for media object reuse (if applicable).
    """
    def __init__(self, 
                 download_strategy: Optional[DownloadingStrategy], 
                 max_workers: int = 1,
                 download_queue_size: int = 10,
                 message_pool_size: int = 10,
                 progress_tracker_callback: Callable = None
                ) -> None:
        self.max_workers = max_workers
        self.download_strategy = download_strategy
        self.progress_tracker_callback = progress_tracker_callback
        self._media_store = MediaFilesBank()

        # Define the template for storing metadata of MediaObjects
        self.media_msg_template = (
            MessageBuilder()
                .add_field("media_object", None)  # Holds the actual MediaObject instance
                .add_field("status", None)  # Represents the message status (queued, done...)
                .add_field("download_method", None)  # Holds the downloading strategy
                .add_field("timestamp", None)   # Time of creation
                .build()
        )

        pool_size = max(message_pool_size, self.max_workers * 2) 
        self._pool = MessagePool(template=self.media_msg_template, max_size=pool_size)

        # Initializing the pulsebus message transaction event driven system
        self.system = EventSystem(queue_size=download_queue_size)
        self.download_enqueuer = DownloadEnqueuer(
            self._pool, 
            self.download_strategy,
            self._media_store
        )
        
        # Setup producers (enqueuers)
        self.system.register_producer(
            self.download_enqueuer,
            name="VideoEnqueuer"
        )
        
        # Setup consumers (workers)
        self.system.register_consumer(
            DownloadWorker(self._pool),
            name="DownloadWorker",
            parallelism=self.max_workers
        )

        self.system.enable_auto_shutdown(2)  # Shutdown system after finishing
        
        # Instantiate the download progress tracker
        self.download_progress_tracker = DownloadProgressTracker(
            printer_fn=self.progress_tracker_callback
        )
        
        self._start()  # Start the event system

    def set_downloading_strategy(self, download_strategy: DownloadingStrategy) -> None:
        """ Sets a downloading strategy to use for downloading a video """
        self.download_strategy = download_strategy
        logger.info(f"Download strategy set to: {download_strategy.__class__.__name__}")
    
    def set_max_workers(self, max_workers: int) -> None:
        """Adjusts the number of workers"""
        if max_workers == self.max_workers:
            return
        self.max_workers = max_workers
    
    def set_status_tracking_hook(self, fn: Optional[Callable]) -> None:
        """ Gives a callable function to display the status tracking data """
        self.progress_tracker_callback = fn

    def get_inuse_message_count(self) -> dict:
        """Returns The pool usage statistics"""
        return self._pool.stats()

    def enqueue_media(self, media_object: MediaObject):
        """ 
        Enqueue a media object for downloading
        
        Args:
            media_object: The media object to download
            
        Returns:
            bool: True if enqueued successfully, False otherwise
        """
        try:
            self._media_store.store(media_object)

        except Exception as e:
            logger.error(f"Failed to enqueue media: {str(e)}")
            return False

    def _start(self):
        """Starts the Event-Driven downloading system"""
        logger.info("Starting Download system")
        self.system.start_all()

    def _shutdown(self):
        """Shuts down the Event-Driven downloading system"""
        self.system.stop_all()  
        logger.info("System stopped. Processing complete.")

    def maintain_system(self):
        """Blocks until all messages are processed and returned to the pool."""
        try:
            pool_stats = self._pool.stats()
            while not (pool_stats["in_use"] == 0 and pool_stats["available"] > 0):
                sleep(2)  # Check every 4 seconds for finished downloads
            
            logger.info("[Manager] All downloads completed.")
        except KeyboardInterrupt:
            logger.info("[Manager] Force shutdown requested!")
        finally:
            # self.download_progress_tracker.shutdown()  # Shutdown the tracker
            self._shutdown()  # Shuts down the system after the downloads are completed
            logger.info("[Manager] Downloader System fully stopped!")

