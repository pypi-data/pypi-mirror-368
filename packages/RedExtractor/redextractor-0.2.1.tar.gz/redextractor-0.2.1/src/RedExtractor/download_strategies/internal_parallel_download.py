from .downloading_strategy import DownloadingStrategy
from core.media_object_class import MediaObject
from core.download_helper import download_media

class ParallelDownload(DownloadingStrategy):
    """
    High-performance parallel download strategy.

    This strategy divides the file into smaller chunks and downloads them
    concurrently using multiple threads or processes. After downloading, it
    merges the chunks into a single complete file.

    This approach significantly improves download speed for large files or
    servers that support HTTP range requests.

    Suitable for:
        - Large files
        - High-bandwidth connections
        - Performance-critical applications

    Features:
        - Concurrent chunk downloading
        - Optimized merging of file parts
        - Error handling and retry logic per chunk (optional)

    This class follows the Strategy design pattern and can be used
    interchangeably with other download strategies.
    """
    def __init__(self) -> None:
        super().__init__()
        self.download_settings.update({
            'windowsfilenames': True,
            'retries': 20,
            'file_access_retries': 10,
            'fragment_retries': 20,
            'extractor_retries': 3,
            'sleep_interval': 1,
            'force_overwrites': True,
            'no_mtime': True,  # Skip file timestamp updates
        })
    
    def __str__(self) -> None:
        return "YTD Lp simple download strategy."
    
    def download(self, media_object: MediaObject, progress_callback=None):

        outtmpl = f"{media_object.output_path}/{media_object.output_name or media_object.title}.%(ext)s"
        file_ext = media_object.file_format
        max_concurrent_frags = 3

        if progress_callback:
            progress_hook = [progress_callback]
            no_progress = True
        else:
            progress_hook = []
            no_progress = False
        
        # set the ytdlp settings/options
        self.download_settings.update({
            "noprogress": no_progress,
            "progress_hooks": progress_hook,
            "format": media_object.format_id,
            "outtmpl": outtmpl,
            "merge_output_format": file_ext,  # Threads per file (for ffmpeg fragment merging)
            # "external_downloader": "aria2c",  # Optional: Use aria2c for better performance
            "concurrent_fragment_downloads": max_concurrent_frags,  # Reduced from 5
            "n_threads": 2,  # Reduced threads for merging
        })

        # Download the video using yt-dlp
        download_media(media_object.url, self.download_settings)
