from .downloading_strategy import DownloadingStrategy
from core.media_object_class import MediaObject
from core.download_helper import download_media

class MP3Download(DownloadingStrategy):
    """
    MP3-specific download strategy.

    This strategy is designed to download audio content and convert or extract it
    into an `.mp3` format if necessary. It may use post-processing tools such as
    FFmpeg to ensure output consistency.

    Suitable for:
        - Music/audio downloads
        - Podcast downloaders
        - Use cases requiring `.mp3` output format

    Features:
        - Downloads only audio streams
        - Converts to `.mp3` if required
        - Lightweight and format-focused

    This class adheres to the Strategy design pattern and can be used
    interchangeably with other download strategies within the same framework.
    """
    def __init__(self) -> None:
        super().__init__()

        # setting up the downloading parameters
        self.download_settings.update({
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "extract_flat": False,  # Changed from True to properly process audio
            "force_generic_extractor": False,  # Let yt-dlp choose best extractor
            "socket_timeout": 30
        })
    
    def __str__(self) -> None:
        return "YTD Lp simple download strategy."
    
    def download(self, media_object: MediaObject, progress_callback=None):

        outtmpl = f"{media_object.output_path}/{media_object.output_name if media_object.output_name != "" else media_object.title}.%(ext)s"
        
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
            "format": f"bestaudio/bestaudio/best",
            "outtmpl": outtmpl,
        })
        
        # Additional fixes for problematic videos
        if media_object.url.startswith(('https://youtube.com', 'https://www.youtube.com')):
            self.download_settings.update({
                'extract_flat': 'in_playlist',  # Special handling for YouTube
                'compat_opts': ['no-youtube-unavailable-videos'],
            })

        # Perform download
        download_media(media_object.url, self.download_settings)
