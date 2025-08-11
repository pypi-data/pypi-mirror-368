"""Stream processing manager for S3 operations."""

import json
import csv
import gzip
import bz2
from typing import Any, TypeVar, Generator, Callable, Optional
from io import TextIOWrapper, BytesIO
from contextlib import contextmanager

from chainsaws.aws.s3.s3_types import StreamConfig
from chainsaws.aws.s3.s3_exception import S3StreamingError

T = TypeVar('T')

class StreamManager:
    """Manager class for S3 streaming operations."""

    def __init__(self, s3_api):
        """Initialize StreamManager.

        Args:
            s3_api: Reference to S3API instance
        """
        self.s3_api = s3_api

    @contextmanager
    def stream_context(self, object_key: str, config: StreamConfig) -> Generator[Any, None, None]:
        """Context manager for stream processing.

        Args:
            object_key: Target object key
            config: Stream configuration

        Example:
            ```python
            config = StreamConfig(
                mode="TEXT",
                encoding='utf-8',
                chunk_size=8192
            )
            with stream_manager.stream_context("logs/app.log", config) as stream:
                for line in stream:
                    process_log_line(line)
            ```
        """
        try:
            stream = self._create_stream_processor(object_key, config)
            yield stream
        except Exception as e:
            if config.get('error_handler'):
                config['error_handler'](e)
            else:
                raise
        finally:
            if hasattr(stream, 'close'):
                stream.close()

    def stream_process(
        self,
        object_key: str,
        processor: Callable[[bytes], T],
        config: Optional[StreamConfig] = None
    ) -> Generator[T, None, None]:
        """Process an object as a stream and generate transformed results.

        Args:
            object_key: Target object key
            processor: Function to process each chunk
            config: Stream configuration

        Yields:
            Transformed data

        Example:
            ```python
            def process_chunk(chunk: bytes) -> dict:
                return json.loads(chunk)

            for item in stream_manager.stream_process("data.json", process_chunk):
                print(item)
            ```
        """
        config = config or StreamConfig(chunk_size=8192)
        
        try:
            for chunk in self.s3_api.stream_object(object_key, config['chunk_size']):
                try:
                    result = processor(chunk)
                    if result is not None:
                        yield result
                except Exception as e:
                    if config.get('error_handler'):
                        config['error_handler'](e)
                    else:
                        raise
        except Exception as e:
            if config.get('error_handler'):
                config['error_handler'](e)
            else:
                raise

    def stream_lines(
        self,
        object_key: str,
        encoding: str = 'utf-8',
        chunk_size: int = 8192,
        keep_ends: bool = False
    ) -> Generator[str, None, None]:
        """Stream an object line by line.

        Args:
            object_key: Target object key
            encoding: Text encoding
            chunk_size: Size of each chunk
            keep_ends: Whether to keep line endings

        Yields:
            Each line of text

        Example:
            ```python
            for line in stream_manager.stream_lines("logs/app.log"):
                process_log_line(line)
            ```
        """
        buffer = ""
        
        for chunk in self.s3_api.stream_object(object_key, chunk_size):
            buffer += chunk.decode(encoding)
            while True:
                line_end = buffer.find('\n')
                if line_end == -1:
                    break
                    
                line = buffer[:line_end + 1] if keep_ends else buffer[:line_end]
                buffer = buffer[line_end + 1:]
                yield line
                
        if buffer:
            yield buffer

    def stream_json(
        self,
        object_key: str,
        chunk_size: int = 8192,
        array_mode: bool = False
    ) -> Generator[dict, None, None]:
        """Stream JSON objects.

        Args:
            object_key: Target object key
            chunk_size: Size of each chunk
            array_mode: JSON array processing mode

        Yields:
            Parsed JSON objects

        Example:
            ```python
            for record in stream_manager.stream_json("data.json"):
                process_record(record)
            ```
        """
        if array_mode:
            # Stream JSON array
            decoder = json.JSONDecoder()
            buffer = ""
            
            for chunk in self.s3_api.stream_object(object_key, chunk_size):
                buffer += chunk.decode('utf-8')
                while buffer:
                    try:
                        obj, index = decoder.raw_decode(buffer)
                        buffer = buffer[index:].lstrip()
                        yield obj
                    except json.JSONDecodeError:
                        break
        else:
            # Stream JSON Lines
            for line in self.stream_lines(object_key, chunk_size=chunk_size):
                if line.strip():
                    yield json.loads(line)

    def stream_csv(
        self,
        object_key: str,
        delimiter: str = ',',
        encoding: str = 'utf-8',
        header: bool = True
    ) -> Generator[dict, None, None]:
        """Stream CSV records.

        Args:
            object_key: Target object key
            delimiter: CSV delimiter
            encoding: File encoding
            header: Whether file includes header

        Yields:
            CSV records as dictionaries

        Example:
            ```python
            for record in stream_manager.stream_csv("data.csv"):
                process_record(record)
            ```
        """
        with self.stream_context(object_key, StreamConfig(
            mode="TEXT",
            encoding=encoding
        )) as stream:
            csv_reader = csv.DictReader(stream, delimiter=delimiter) if header else csv.reader(stream, delimiter=delimiter)
            yield from csv_reader

    def _create_stream_processor(self, object_key: str, config: StreamConfig) -> Any:
        """Create a stream processor.

        Args:
            object_key: Target object key
            config: Stream configuration

        Returns:
            Stream processor object
        """
        try:
            raw_stream = self.s3_api.stream_object(object_key, config['chunk_size'])
            
            # Handle compression
            if config.get('compression'):
                if config['compression'] == 'gzip':
                    stream = gzip.GzipFile(fileobj=BytesIO(raw_stream))
                elif config['compression'] == 'bzip2':
                    stream = bz2.BZ2File(BytesIO(raw_stream))
                else:
                    raise ValueError(f"Unsupported compression: {config['compression']}")
            else:
                stream = raw_stream

            # Process by mode
            if config['mode'] == "TEXT":
                return TextIOWrapper(stream, encoding=config.get('encoding', 'utf-8'))
            elif config['mode'] == "BINARY":
                return stream
            elif config['mode'] == "JSON":
                return self.stream_json(stream)
            elif config['mode'] == "CSV":
                return self.stream_csv(stream, delimiter=config.get('delimiter', ','))
            
            raise ValueError(f"Unsupported mode: {config['mode']}")
        except Exception as e:
            raise S3StreamingError(object_key=object_key, reason=str(e)) from e 