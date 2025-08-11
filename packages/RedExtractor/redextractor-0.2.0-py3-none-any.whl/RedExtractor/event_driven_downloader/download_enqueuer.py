from pulsebus import BaseProducer, MessagePool
from utils.logger import logger
from utils.media_files_bank import MediaFilesBank
from progress_tracking.progress_tracking import DownloadingState

from time import time

class DownloadEnqueuer(BaseProducer):
    """
    A producer class in an event-driven download system responsible for enqueuing media tasks.

    The `DownloadEnqueuer` acts as the entry point of the download pipeline. It receives
    media objects (e.g., video, audio, or file metadata) and publishes them into a
    shared message queue or task bus for downstream consumers to process (e.g., downloaders,
    validators, or format converters).

    This design allows for full decoupling between download task submission and processing,
    enabling scalable, concurrent, and reactive download systems.

    Responsibilities:
        - Accept media task objects (files, metadata, etc.)
        - Enqueue/publish them to a shared queue (e.g., PulseBus, asyncio.Queue, etc.)
        - Optionally validate or enrich media objects before enqueueing
        - Ensure media tasks are pushed in FIFO order for predictable processing

    Typical usage:
        enqueuer = DownloadEnqueuer(queue=task_queue)
        enqueuer.produce(media_object)
    """
    def __init__(self, pool: MessagePool, strategy, media_store: MediaFilesBank):
        self._pool = pool
        self.download_strategy = strategy
        self._temp_media_bank = media_store  # Temporary holding for manager-injected messages

    def on_start(self):
        logger.info(f"DownloadEnqueuer started!")
             
    def on_stop(self):
        logger.info(f"DownloadEnqueuer stopped!")
    
    def produce(self):
        """Called by PulseBus when ready for new messages"""
        if not self._temp_media_bank.is_empty():
            media_object = self._temp_media_bank.retrieve()

            # Acquires a message template and fills with data
            msg = self._pool.acquire()  # Block if no slots available

            msg.set_property("media_object", media_object)
            msg.set_property("status", DownloadingState.QUEUED)
            msg.set_property("download_method", self.download_strategy)
            msg.set_property("timestamp", time())

            return msg  # Push message in pulsebus queue         
        
        return 23
        