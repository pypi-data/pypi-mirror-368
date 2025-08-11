from dataclasses import dataclass, asdict

@dataclass
class MediaObject:
    """
    Data class that structures the necessary downloading file data 
    ' video ' or ' audio ' to model a DataBase.

    Attributes:
        url (str): The URL of the media to download.
        title (str): The media title. 
        output_path (str): The file path where the downloaded media will be saved.
        output_name (str): The file final name/title.
        format_id (str): The media file copy/variation.
        file_format (str): The format of the file to be downloaded (e.g., 'mp4', 'mp3').
        Chunk_size (int): The maximum size (in bytes) for each chunk of the download.
    """

    __url: str
    __title: str
    __output_path: str
    __output_name: str
    __file_format: str
    __format_id: str = "bestvideo+bestaudio/best"  # Best format by default
    __CHUNK_SIZE: int = 1024 * 1024  # 1 MB per chunk

    @property
    def url(self) -> str:
        """
        Gets the URL of the media to download.
        
        Returns:
            str: The URL of the media.
        """
        return self.__url

    @url.setter
    def url(self, value: str) -> None:
        """
        Sets the URL of the media to download.
        
        Args:
            value (str): The new URL of the media.
        """
        self.__url = value

    @property
    def output_path(self) -> str:
        """
        Gets the output path where the downloaded media will be saved.
        
        Returns:
            str: The output path.
        """
        return self.__output_path

    @output_path.setter
    def output_path(self, value: str) -> None:
        """
        Sets the output path where the downloaded media will be saved.
        
        Args:
            value (str): The new output path.
        """
        self.__output_path = value

    @property
    def title(self) -> str:
        """
        Gets the title of the media file to download.
        
        Returns:
            str: The title of the media.
        """
        return self.__title

    @title.setter
    def title(self, value: str) -> None:
        """
        Sets the title of the media file to download.
        
        Args:
            value (str): The new title of the media file.
        """
        self.__title = value

    @property
    def output_name(self) -> str:
        """
        Gets the output_name of the media file to download.
        
        Returns:
            str: The output_name of the media file.
        """
        return self.__output_name

    @output_name.setter
    def output_name(self, value: str) -> None:
        """
        Sets the output_name of the media file to download.
        
        Args:
            value (str): The new output_name of the media file.
        """
        self.__output_name = value

    @property
    def format_id(self) -> str:
        """
        Gets the format_id of the media file to download.
        
        Returns:
            str: The format_id of the media file.
        """
        return self.__format_id

    @format_id.setter
    def format_id(self, value: str) -> None:
        """
        Sets the format_id of the media file to download.
        
        Args:
            value (str): The new format_id of the media file.
        """
        self.__format_id = value
        
    @property
    def file_format(self) -> str:
        """
        Gets the format of the file to be downloaded.
        
        Returns:
            str: The file format (e.g., 'mp4', 'mp3', 'WEBM', 'AAC').
        """
        return self.__file_format

    @file_format.setter
    def file_format(self, value: str) -> None:
        """
        Sets the format of the file to be downloaded.
        
        Args:
            value (str): The new file format (e.g., 'mp4', 'mp3', 'WEBM', 'AAC').
        """
        self.__file_format = value

    @property
    def CHUNK_SIZE(self) -> int:
        """
        Gets the maximum size for each chunk of the download.
        
        Returns:
            int: The maximum chunk size in bytes.
        """
        return self.__CHUNK_SIZE

    def get_object_data(self) -> str:
        """Serialize the object to a JSON string."""
        return asdict(self)
