import unittest
from unittest.mock import patch, MagicMock
from download_strategies.basic_download import SimpleDownload, MediaObject  # Adjust import as needed

class TestSimpleDownload(unittest.TestCase):
    
    def setUp(self):
        self.downloader = SimpleDownload()
        self.media_object = MediaObject(
            "https://www.youtube.com/watch?v=4Cf2fsFBGe0&list=WL&index=10",
            "Good",
            "C:/Users/flame/Videos/Captures",
            "crav",
            "bestvideo",
            "mp4",
            21
        )
    
    @patch("download_strategies.basic_download.download_media")
    def test_download(self, mock_download_media):
        mock_download_media.return_value = None  # Mock successful call
        
        self.downloader.download(self.media_object, throttle_rate="500M")
        
        mock_download_media.assert_called_once_with(
            self.media_object.url, {
                "format": "bestvideo+bestaudio/best",
                "no_color": True,
                "noplaylist": True,
                "skip_download": False,
                "no_warnings": True,
                "no_call_home": True,
                "source_address": None,
                "outtmpl": f"{self.media_object.output_path}/%(title)s.%(ext)s",
                "throttled_rate": "500M"
            }
        )
    
    def test_str_representation(self):
        self.assertEqual(str(self.downloader), "YTD Lp simple download strategy.")

if __name__ == "__main__":
    unittest.main()
