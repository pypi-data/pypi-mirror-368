import unittest
from unittest.mock import patch, MagicMock
from download_strategies.mp3_format_download import MP3Download, MediaObject, download_media  # Adjust import paths as needed

class TestMP3Download(unittest.TestCase):
    
    def setUp(self):
        self.downloader = MP3Download()
        self.media_object = MediaObject(
            "https://www.youtube.com/watch?v=4Cf2fsFBGe0&list=WL&index=10",
            "Good",
            "C:/Users/flame/Videos/Captures",
            "crav",
            "bestaudio",
            "mp3",
            21
        )
    
    @patch("download_strategies.mp3_format_downloader.download_media")  # Mocking download_media function
    def test_download_calls_download_media(self, mock_download_media):
        """Test that download_media is called with correct parameters."""
        self.downloader.download(self.media_object)
        
        expected_settings = {
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "quiet": True,
            "format": "bestaudio/bestaudio/best",
            "outtmpl": "C:/Users/flame/Videos/Captures/%(title)s.%(ext)s"
        }
        mock_download_media.assert_called_once_with(self.media_object.url, expected_settings)
    
    def test_string_representation(self):
        """Test the __str__ method."""
        self.assertEqual(str(self.downloader), "YTD Lp simple download strategy.")

if __name__ == "__main__":
    unittest.main()
