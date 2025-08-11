from enum import Enum
from typing import Union


class FileType(Enum):
    """Supported file types"""
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"
    FILE = "FILE"


class File:
    """Definition of File"""
    
    def __init__(self, file_id: str, type: Union[str, FileType]):
        """
        Constructs a File instance with specified file ID and file type
        
        Args:
            file_id: Unique file ID obtained from File Upload API
            type: File type (IMAGE/AUDIO/VIDEO/FILE)
        """
        self.file_id = file_id
        self.type = type if isinstance(type, str) else type.value
    
    def get_file_id(self) -> str:
        """
        Get the file ID
        
        Returns:
            File ID string
        """
        return self.file_id
    
    def set_file_id(self, file_id: str) -> None:
        """
        Update the file ID
        
        Args:
            file_id: uploaded file ID via File Upload API
        """
        self.file_id = file_id
    
    def get_type(self) -> str:
        """
        Get the file type
        
        Returns:
            File type (IMAGE/AUDIO/VIDEO/FILE)
        """
        return self.type
    
    def set_type(self, type: Union[str, FileType]) -> None:
        """
        Update the file type
        
        Args:
            type: supported types include IMAGE, AUDIO, VIDEO, FILE
        """
        self.type = type if isinstance(type, str) else type.value
