from pulsebus import MessagePool, MessageTemplate, BaseConsumer

from progress_tracking.progress_tracking import DownloadingState, progress_hook
from utils.logger import logger

class DownloadWorker(BaseConsumer):
    """
    A consumer class in an event-driven download system responsible for downloading media.

    The `DownloadWorker` acts as the core consumer in a producer-consumer architecture.
    It listens to a shared task queue where media download jobs are published by a producer
    (e.g., `DownloadEnqueuer`), retrieves tasks in FIFO order, and processes them by
    executing the actual download logic.

    This class represents the **execution stage** of the pipeline. It decouples the download
    logic from task submission and enables concurrent or distributed downloading by allowing
    multiple worker instances to operate independently on the same queue.

    Responsibilities:
        - Retrieve (pop) media objects from the shared queue
        - Execute the download operation using a selected download strategy
        - Report status and progress (e.g., via hooks, callbacks, or tracker)
        - Optionally handle retries, errors, and post-download processing

    Typical usage:
        worker = DownloadWorker(queue=task_queue, strategy=ParallelDownloadStrategy())
        worker.start()
    """
    def __init__(self, pool: MessagePool):
        self._pool = pool
        self.progress_hook = progress_hook

    def on_start(self):
        logger.info(f"DownloadWorker started!")
    
    def on_stop(self):
        logger.info(f"DownloadWorker stopped!")
    
    def consume(self, msg: MessageTemplate):
        if not isinstance(msg, MessageTemplate):
            return
        try:

            # Unpack message data
            media_object = msg.get_property("media_object")
            download_strategy = msg.get_property("download_method")

            logger.debug(f"Processing: {media_object.output_name} (Worker: {id(self)})")
            msg.set_property("status", DownloadingState.IN_PROGRESS)

            # download media file
            download_strategy.download(  
                media_object, self.progress_hook
            )

            # Update status to COMPLETED
            msg.set_property("status", DownloadingState.COMPLETED)
            logger.info(f"Completed download: {media_object.output_name}")
        except Exception as e:
            logger.error(f"Failed to download {media_object}: {str(e)}")
            msg.set_property("status", DownloadingState.FAILED)
        finally:
            self._pool.release(msg)  # Release message after done

            logger.info(f"Message released: {media_object.output_name}")
            logger.info(f"STATS AFTER DK RE: {self._pool.stats()}, {id(self._pool)}")
