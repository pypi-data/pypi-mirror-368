import unittest
from unittest.mock import patch, AsyncMock
import asyncio
from download_strategies.merge_download import MergingDownload, MediaObject  # Replace 'your_module' with the actual module name

class TestMergingDownload(unittest.TestCase):
    
    @patch("download_strategies.merge_download.download_media_separately", new_callable=AsyncMock)
    def test_download(self, mock_download_media_separately):
        mock_download_media_separately.return_value = "output_path/file.mp4"
        
        media_object = MediaObject(
            "https://www.youtube.com/watch?v=4Cf2fsFBGe0&list=WL&index=10",
            "Good",
            "C:/Users/flame/Videos/Captures",
            "crav",
            "bestvideo",
            "mp4",
            21
        )
        
        downloader = MergingDownload()
        
        # Run async method inside the event loop
        asyncio.run(downloader.download(media_object))
        
        # Verify the method was called with correct arguments
        mock_download_media_separately.assert_called_once_with(
            media_object.url,
            media_object.output_path,
            video_format=media_object.format_id,
            audio_format="bestaudio[ext=m4a]"
        )

if __name__ == "__main__":
    unittest.main()
