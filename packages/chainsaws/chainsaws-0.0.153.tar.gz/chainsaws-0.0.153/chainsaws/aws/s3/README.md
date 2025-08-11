# AWS S3 Client Wrapper

A high-level Python wrapper for AWS S3 operations with enhanced features and type safety.

## Features

- 🚀 High-level API for common S3 operations
- 📁 Directory operations (upload, download, sync)
- 🔄 Batch operations with parallel processing
- 📊 Progress tracking and retry mechanisms
- ⚡ Transfer acceleration support
- 🔍 Pattern-based object search
- 🔒 Type-safe interfaces with TypedDict and Literal types
- 🛠️ No need for separate imports - everything included

## Installation

```bash
pip install chainsaws
```

## Quick Start

```python
from chainsaws.aws.s3 import S3API

# Initialize S3 client
s3 = S3API(bucket_name="my-bucket")

# 🎯 Super simple upload/download
s3.put("hello.txt", "Hello, World!")  # Upload text
content = s3.get("hello.txt")  # Download to memory
s3.get("hello.txt", "local.txt")  # Download to file

# 🎯 File operations made easy
if s3.exists("important.txt"):
    s3.copy("important.txt", "backup.txt")
    s3.delete("old-file.txt")

# 🎯 List files with simple interface
for obj in s3.list("logs/", limit=100):
    print(f"Found: {obj['Key']}, Size: {obj['Size']}")
```

## ✨ New Simple Interface

### Basic Operations

```python
# Upload - auto-detects content type from 80+ file extensions!
s3.put("data.json", {"key": "value"})           # application/json
s3.put("document.pdf", pdf_bytes)               # application/pdf
s3.put("archive.zip", zip_data)                 # application/zip
s3.put("script.py", python_code)                # text/x-python
s3.put("README.md", markdown_text)              # text/markdown
s3.put("config.yaml", yaml_config)              # text/yaml
s3.put("photo.jpg", image_bytes)                # image/jpeg
s3.put("video.mp4", video_data)                 # video/mp4
s3.put("music.mp3", audio_bytes)                # audio/mpeg
s3.put("font.ttf", font_data)                   # font/ttf

# Manual content type override when needed
s3.put("special.bin", binary_data, content_type="application/octet-stream")
s3.put("custom.xyz", data, content_type="application/json")  # Force JSON

# All file operations support wide range of formats
exists = s3.exists("presentation.pptx")         # PowerPoint
size = s3.size("archive.7z")                    # 7-Zip archive
s3.copy("source.cpp", "backup.cpp")             # C++ source
s3.delete("old.mkv")                            # Matroska video

# Download - flexible interface with explicit options
content = s3.get("data.json")  # To memory
s3.get("data.json", "local.json")  # To file
s3.get("large.zip", "local.zip", max_retries=5, chunk_size=16*1024*1024)  # Custom settings

# List with pagination support
for obj in s3.list("logs/", limit=100, start_after="logs/2024-01-01"):
    print(f"Found: {obj['Key']}")

# Get file info and tags
info = s3.info("file.txt")
print(f"Size: {info['ContentLength']}, Modified: {info['LastModified']}")

current_tags = s3.tags("file.txt")  # Get tags
s3.tags("file.txt", {"env": "prod", "version": "1.0"})  # Set tags
```

### Smart Upload

```python
# Unified upload method with clear parameters
s3.upload("small.txt", "Hello")  # Uses simple upload
s3.upload("big.zip", large_data, large_file=True, part_size=10*1024*1024)  # Custom multipart
s3.upload("auto.zip", data, progress_callback=lambda current, total: print(f"{current/total*100:.1f}%"))
```

### Presigned URLs

```python
# Simple URL generation with explicit expiration
download_url = s3.url("file.pdf", expiration=7200)  # 2 hours
upload_url = s3.upload_url("new-file.jpg", content_type="image/jpeg", expiration=3600)

# Use in your app
print(f"Download here: {download_url}")
```

### Easy Queries

```python
# Query JSON Lines files
for record in s3.query_json("logs.jsonl", "SELECT * WHERE level='ERROR'"):
    print(f"Error: {record}")

# Query CSV files
for user in s3.query_csv("users.csv", "SELECT name, email WHERE age > 25"):
    print(f"User: {user['name']} - {user['email']}")

# Custom CSV settings
for record in s3.query_csv("data.csv", "SELECT * FROM s3object",
                          has_header=False, delimiter="|"):
    print(record)
```

### Batch Operations

```python
# Upload multiple files with worker control
items = [
    {"key": "file1.txt", "data": "content1"},
    {"key": "file2.txt", "data": "content2"},
    {"key": "data.json", "data": {"key": "value"}, "content_type": "application/json"}
]
result = s3.put_many(
    items,
    max_workers=4,
    progress_callback=lambda file_key, current, total: print(f"{file_key}: {current/total*100:.1f}%")
)

# Download multiple files with explicit settings
keys = ["file1.txt", "file2.txt", "data.json"]
result = s3.get_many(
    keys,
    "./downloads",
    max_workers=4,
    chunk_size=16*1024*1024,
    progress_callback=lambda file_key, current, total: print(f"Downloading {file_key}...")
)

# Delete multiple files
result = s3.delete_many(["old1.txt", "old2.txt", "temp.txt"])
print(f"Deleted: {result['successful']}")
print(f"Failed: {result['failed']}")
```

## Advanced Usage

### Original Interface (Still Available)

All the original methods are still available for advanced use cases:

```python
# Original detailed interface still works
result = s3.upload_file(
    object_key="file.txt",
    file_bytes=data,
    config={
        "content_type": "text/plain",
        "acl": "public-read"
    }
)

# Advanced multipart upload
result = s3.upload_large_file(
    object_key="big-file.zip",
    file_bytes=large_data,
    content_type="application/zip",
    part_size=10 * 1024 * 1024,  # 10MB parts
    progress_callback=lambda current, total: print(f"Progress: {current/total*100:.1f}%")
)
```

## Configuration Made Simple

Main configurations use TypedDict for easy usage, while API configuration uses dataclass:

```python
# S3 API configuration (dataclass)
from chainsaws.aws.s3 import S3API, S3APIConfig

config = S3APIConfig(
    region="us-west-2",
    acl="private",
    use_accelerate=True
)
s3 = S3API(bucket_name="my-bucket", config=config)

# Or use the helper function
from chainsaws.aws.s3 import create_s3_api_config

config = create_s3_api_config(
    region="us-west-2",
    acl="public-read"
)
s3 = S3API(bucket_name="my-bucket", config=config)

# Upload/Download configurations (TypedDict - no imports needed!)
s3.upload_file(
    object_key="image.jpg",
    file_bytes=image_data,
    config={
        "content_type": "image/jpeg",
        "acl": "public-read"
    }
)

# Download configuration
s3.download_file(
    object_key="large-file.zip",
    file_path="./downloads/file.zip",
    config={
        "max_retries": 5,
        "retry_delay": 2.0,
        "chunk_size": 16 * 1024 * 1024  # 16MB chunks
    }
)
```

## Helper Functions

Use built-in helper functions for convenient configuration:

```python
from chainsaws.aws.s3 import (
    S3API,
    create_upload_config,
    create_download_config,
    get_content_type_from_extension
)

# Create configurations with defaults
upload_config = create_upload_config(
    content_type="application/json",
    acl="public-read"
)

download_config = create_download_config(
    max_retries=10,
    chunk_size=32 * 1024 * 1024
)

# Auto-detect content type
content_type = get_content_type_from_extension("pdf")  # Returns "application/pdf"
```

## Directory Operations

### Upload Directory

```python
# Upload entire directory
result = s3.upload_directory(
    local_dir="./data",
    prefix="backup/2024",
    exclude_patterns=["*.tmp", "**/__pycache__/*"]
)

# Check results
for success in result["successful"]:
    print(f"Uploaded: {success['url']}")
for failed in result["failed"]:
    print(f"Failed: {list(failed.keys())[0]}")
```

### Download Directory

```python
# Download directory with pattern matching
s3.download_directory(
    prefix="backup/2024",
    local_dir="./restore",
    include_patterns=["*.json", "*.csv"]
)
```

### Directory Sync

```python
# Sync local directory with S3
result = s3.sync_directory(
    local_dir="./website",
    prefix="static",
    delete=True  # Delete files that don't exist locally
)

print(f"Uploaded: {len(result['uploaded'])} files")
print(f"Updated: {len(result['updated'])} files")
print(f"Deleted: {len(result['deleted'])} files")
```

## Batch Operations

### Bulk Upload

```python
# Simple bulk upload with TypedDict
items = [
    {
        "object_key": "file1.txt",
        "data": b"content1",
        "content_type": "text/plain"
    },
    {
        "object_key": "file2.json",
        "data": b'{"key": "value"}',
        "content_type": "application/json"
    }
]

result = s3.bulk_upload(
    items,
    config={
        "max_workers": 4,
        "progress_callback": lambda key, current, total: print(f"{key}: {current/total*100:.1f}%")
    }
)
```

### Multiple File Download

```python
result = s3.download_multiple_files(
    object_keys=["file1.txt", "file2.txt"],
    output_dir="./downloads",
    config={"max_workers": 4}
)

for success in result["successful"]:
    print(f"Downloaded {success['object_key']} to {success['local_path']}")
```

## Object Search

```python
# Find objects using glob patterns
for obj in s3.find_objects(
    pattern="logs/**/error*.log",
    recursive=True,
    max_items=100
):
    print(f"Found: {obj['Key']} (Size: {obj['Size']} bytes)")
```

## Advanced Features

### Transfer Acceleration

```python
# Enable transfer acceleration
if s3.enable_transfer_acceleration():
    print("Transfer acceleration enabled")

# Automatically optimize transfer settings
s3.optimize_transfer_settings()
```

### Presigned URLs

```python
# Generate presigned URL for upload
upload_url = s3.create_presigned_url_put_object(
    object_key="upload/file.txt",
    expiration=3600  # 1 hour
)

# Generate presigned URL for download
download_url = s3.create_presigned_url_get_object(
    object_key="download/file.txt",
    expiration=3600
)
```

### Object Tags and Metadata

```python
# Get object tags
tags = s3.get_object_tags("path/to/file.txt")

# Set object tags
s3.put_object_tags("path/to/file.txt", {
    "environment": "production",
    "version": "1.0"
})

# Get object metadata
metadata = s3.get_object_metadata("path/to/file.txt")
```

### Streaming Support

```python
# Stream large objects
for chunk in s3.stream_object("large-file.dat"):
    process_chunk(chunk)

# Stream with configuration
config = {
    "mode": "TEXT",
    "encoding": "utf-8",
    "chunk_size": 8192
}

with s3.stream.stream_context("logs/app.log", config) as stream:
    for line in stream:
        process_log_line(line)
```

## S3 Select Queries

```python
# Query JSON Lines with simple syntax
results = s3.select_query(
    object_key="data/logs.jsonl",
    query="SELECT * FROM s3object s WHERE s.level = 'ERROR'",
    input_format="JSON",
    json_type="LINES"
)

for record in results:
    print(record)

# Query CSV with custom configuration
results = s3.select_query(
    object_key="data/users.csv",
    query="SELECT name, email FROM s3object WHERE age > 25",
    input_format="CSV",
    csv_input_config={
        "file_header_info": "USE",
        "delimiter": ","
    }
)
```

## Error Handling

The library provides detailed error information through custom exceptions:

```python
from chainsaws.aws.s3 import S3StreamingError, S3MultipartUploadError

try:
    s3.upload_large_file("large.zip", file_bytes)
except S3MultipartUploadError as e:
    print(f"Upload failed: {e.reason}")
    print(f"Object key: {e.object_key}")
    print(f"Upload ID: {e.upload_id}")
```

## Type Safety

All operations are fully typed with TypedDict and Literal types:

```python
from typing import TypedDict
from chainsaws.aws.s3 import (
    S3API,
    UploadConfig,
    DownloadConfig,
    DirectoryUploadResult,
    ContentType
)

# Type hints work perfectly
def process_upload_result(result: DirectoryUploadResult) -> None:
    for success in result["successful"]:
        print(f"URL: {success['url']}")

# Content types are Literal strings
content_type: ContentType = "application/json"  # Fully typed!
```

## Migration Guide

### Before (dataclass/Enum style):

```python
from chainsaws.aws.s3 import S3API, UploadConfig, ContentType

config = UploadConfig(
    content_type=ContentType.JSON,
    acl="private"
)
s3.upload_file("file.json", data, config)
```

### After (TypedDict/Literal style):

```python
from chainsaws.aws.s3 import S3API

# No imports needed for config!
s3.upload_file(
    "file.json",
    data,
    config={
        "content_type": "application/json",
        "acl": "private"
    }
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Supported File Types (80+ Extensions!)

The S3 API automatically detects content types for a wide variety of file formats:

### 📄 Documents & Office

- **Text**: txt, log, md, yaml, yml, xml, csv, html, css
- **Microsoft Office**: doc, docx, xls, xlsx, ppt, pptx
- **Other Documents**: pdf, rtf, epub, mobi

### 💻 Programming & Scripts

- **Web**: js, mjs, ts, html, css
- **Languages**: py, java, c, cpp, cs, php, rb, go, rs, swift, kt, scala
- **Scripts**: sh, bash, bat, cmd, sql
- **Config**: json, yaml, yml, toml, ini, conf, dockerfile

### 🗜️ Archives & Compressed

- **Common**: zip, gz, gzip, tar, rar, 7z
- **Executables**: exe, msi, dmg, apk

### 🖼️ Images

- **Web**: jpg, jpeg, png, gif, svg, webp, avif
- **Professional**: bmp, tiff, tif, ico, heic
- **RAW**: cr2, crw, nef (Camera RAW formats)

### 🎵 Audio

- **Lossless**: flac, wav, aiff
- **Compressed**: mp3, aac, m4a, ogg, opus, wma

### 🎬 Video

- **Web**: mp4, webm, m4v
- **Professional**: mov, avi, mkv, wmv, flv
- **Mobile**: 3gp, 3g2

### 🔤 Fonts

- **Modern**: ttf, otf, woff, woff2

```python
# Examples with various file types
s3.put("app.js", javascript_code)               # application/javascript
s3.put("data.py", python_script)                # text/x-python
s3.put("backup.tar.gz", compressed_data)        # application/gzip
s3.put("presentation.pptx", powerpoint_data)    # application/vnd.openxml...
s3.put("photo.heic", iphone_photo)              # image/heic
s3.put("song.flac", lossless_audio)             # audio/flac
s3.put("movie.mkv", video_file)                 # video/x-matroska
s3.put("font.woff2", web_font)                  # font/woff2
```
