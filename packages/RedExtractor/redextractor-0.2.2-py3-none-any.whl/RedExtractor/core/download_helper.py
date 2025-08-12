from typing import Any
from utils.logger import logger

def download_media(url: str,
    extractor_settings: dict[str, Any],
    max_retries: int = 3,
    backoff_seconds: int = 2
) -> bool:
    """
    Downloads a YouTube video with retry logic for handling transient failures.

    Implements exponential backoff (fixed here but easily modifiable) and
    separates YouTube-specific errors from generic exceptions.

    Args:
        url: YouTube video URL to download.
        extractor_settings: yt-dlp configuration (e.g., format, output template).
        max_retries: Maximum attempts before giving up (default: 3).
        backoff_seconds: Delay between retries in seconds (default: 2).

    Returns:
        bool: True if download succeeded, False if all retries failed.

    Example:
        >>> settings = {"format": "bestvideo+bestaudio"}
        >>> download_media("https://youtu.be/example", settings)
    """
    
    # Import necessary libraries
    import yt_dlp
    from time import sleep

    attempts = 0
    while attempts <= max_retries:
        try:  # Start downloading
            with yt_dlp.YoutubeDL(extractor_settings) as ydl:
                ydl.download([url])
            return True  # Success

        except yt_dlp.utils.DownloadError as e:  # Handle any download error
            # YouTube-specific error (e.g., geo-restriction, removed video)
            logger.exception(f"Download failed (attempt {attempts + 1}/{max_retries}): {e}")
            attempts += 1
            if attempts <= max_retries:
                sleep(backoff_seconds)

        except Exception as e:  # Handle any other occuring exception
            # Network issues, filesystem errors, etc.
            logger.exception(f"Unexpected error downloading {url}: {e}")
            return False  # Immediate fail for non-retryable errors
        
    logger.error(f"Max retries ({max_retries}) reached for {url}. Aborting.")
    return False