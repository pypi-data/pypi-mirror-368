from .downloading_strategy import DownloadingStrategy
from core.media_object_class import MediaObject
from core.download_helper import download_media

class SimpleDownload(DownloadingStrategy):
    """
    Basic file downloading strategy.

    This strategy implements a straightforward, single-threaded download process.
    It retrieves the file in one continuous stream without any form of parallelism
    or post-processing.

    This is the most compatible and lightweight strategy and is ideal for simple
    downloads that do not require high performance or format conversion.

    Suitable for:
        - General-purpose file downloads
        - Environments with limited resources or strict simplicity requirements

    This class can be used interchangeably with other strategies following the
    Strategy design pattern by implementing a common download interface or method,
    such as `download(media_object)`.
    """
    def __init__(self) -> None:
        super().__init__()
    
    def __str__(self) -> None:
        return "YTD Lp simple download strategy."
    
    def download(self, media_object: MediaObject, progress_callback=None):
        
        outtmpl = f"{media_object.output_path}/{media_object.output_name if media_object.output_name != "" else media_object.title}.%(ext)s"
        file_ext = media_object.file_format
        
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
            "merge_output_format": file_ext,
        })

        # Download the video using yt-dlp
        download_media(media_object.url, self.download_settings)

                
