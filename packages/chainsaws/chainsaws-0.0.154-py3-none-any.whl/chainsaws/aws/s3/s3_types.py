from typing import TypedDict, Optional, Callable, Any, Literal


StreamProcessingMode = Literal["BINARY", "TEXT", "JSON", "CSV"]


class StreamConfig(TypedDict, total=False):
    """Stream configuration settings"""
    
    chunk_size: int  # Size of each chunk in bytes
    mode: StreamProcessingMode  # Processing mode
    encoding: str  # Text encoding
    delimiter: str  # Delimiter for CSV/JSON Lines
    compression: Optional[str]  # Compression type (gzip, bzip2, etc.)
    error_handler: Optional[Callable[[Exception], Any]]  # Error handler function 