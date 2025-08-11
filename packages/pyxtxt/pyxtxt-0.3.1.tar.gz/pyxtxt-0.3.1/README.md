# PyxTxt

[![PyPI version](https://img.shields.io/pypi/v/pyxtxt.svg)](https://pypi.org/project/pyxtxt/)
[![Python versions](https://img.shields.io/pypi/pyversions/pyxtxt.svg)](https://pypi.org/project/pyxtxt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**PyxTxt** is a simple and powerful Python library to extract text from various file formats.  
It supports PDF, DOCX, XLSX, PPTX, ODT, HTML, XML, TXT, legacy Office files, **audio/video transcription**, **OCR from images**, and more.

**NEW in v0.2.4**: Added video transcription support! Now supports both audio and video files using Whisper.

---

## ✨ Features

- **Multiple input types**: File paths, `io.BytesIO` buffers, raw `bytes` objects, and `requests.Response` objects
- **Wide format support**: PDF, DOCX, PPTX, XLSX, ODT, HTML, XML, TXT, Markdown, EPUB, RTF, EML, MSG, LaTeX, legacy Office files (.xls, .ppt, .doc)
- **Audio & Video transcription**: MP3, WAV, M4A, FLAC, MP4, MOV, AVI, WebM, MKV and more using OpenAI Whisper
- **OCR from images**: JPEG, PNG, TIFF, BMP using EasyOCR with multilingual support
- **Automatic MIME detection**: Uses `python-magic` for intelligent file type recognition
- **Web-ready**: Direct support for downloading and extracting text from URLs
- **Memory efficient**: Process files without saving to disk
- **Modern Python**: Full type hints and clean API design

---

## 📦 Installation 

The library is modular so you can install all modules:

```bash
pip install pyxtxt[all]
```
or just the modules you need:
```bash
pip install pyxtxt[pdf,docx,presentation,spreadsheet,html,markdown,epub,email]
```

### Audio & OCR (Heavy Dependencies)
```bash
# Audio transcription (~2GB download for Whisper models)
pip install pyxtxt[audio]

# Traditional OCR from images (~1GB download for EasyOCR models)
pip install pyxtxt[ocr]

# AI-powered OCR via Ollama (requires local Ollama + gemma3:4b model)
pip install pyxtxt[ocr-ollama]

# Both audio and traditional OCR
pip install pyxtxt[audio,ocr]
```

Because needed libraries are common, installing the html module will also enable SVG and XML support.
The architecture is designed to grow with new modules for additional formats.
## ⚠️ Note: You must have libmagic installed on your system (required by python-magic).
The pyproject.toml file should select the correct version for your system. But if you have any problem you can install it manually.

**On Ubuntu/Debian:**

```bash
sudo apt install libmagic1
```

**On Mac (Homebrew):**

```bash
brew install libmagic
```
**On Windows:**

Use python-magic-bin instead of python-magic for easier installation.

## 🛠️ Dependencies

### Core Dependencies
- python-magic (automatic file type detection)

### Optional Dependencies by Format
- **PDF**: PyMuPDF
- **Office**: python-docx, python-pptx, openpyxl, xlrd
- **Web/HTML**: beautifulsoup4, lxml
- **OpenDocument**: odfpy
- **Markdown**: markdown
- **EPUB**: ebooklib
- **RTF**: striprtf
- **Email**: extract-msg (for MSG files)
- **LaTeX**: pylatexenc
- **Audio**: openai-whisper (heavy ~2GB models)
- **OCR**: easyocr, pillow (heavy ~1GB models)
- **OCR-Ollama**: ollama, pillow (requires local Ollama server)

Dependencies are automatically installed based on selected optional groups.

## 📚 Usage Examples

### Basic Usage
```python
from pyxtxt import xtxt

# Extract from file path
text = xtxt("document.pdf")
print(text)

# Extract from BytesIO buffer
import io
with open("document.docx", "rb") as f:
    buffer = io.BytesIO(f.read())
text = xtxt(buffer)
print(text)
```

### NEW: Web Content Support
```python
import requests
from pyxtxt import xtxt, xtxt_from_url

# Method 1: Direct from bytes
response = requests.get("https://example.com/document.pdf")
text = xtxt(response.content)

# Method 2: Direct from Response object  
text = xtxt(response)

# Method 3: URL helper function
text = xtxt_from_url("https://example.com/document.pdf")
```

### Audio & Video Transcription (NEW)
```python
from pyxtxt import xtxt

# Transcribe audio files
text = xtxt("meeting_recording.mp3")
text = xtxt("interview.wav")
text = xtxt("podcast.m4a")

# Transcribe video files (extracts audio)
text = xtxt("presentation.mp4")
text = xtxt("conference_video.mov")
text = xtxt("webinar.avi")

# From web audio/video
import requests
audio_response = requests.get("https://example.com/audio.mp3")
text = xtxt(audio_response.content)

video_response = requests.get("https://example.com/video.mp4")
text = xtxt(video_response.content)
```

### OCR from Images (NEW)
```python
from pyxtxt import xtxt

# Traditional OCR with EasyOCR (install with: pip install pyxtxt[ocr])
text = xtxt("scanned_document.png")
text = xtxt("screenshot.jpg")
text = xtxt("invoice.tiff")

# AI-powered OCR with Ollama (install with: pip install pyxtxt[ocr-ollama])
# Requires: ollama server running + gemma3:4b model
from pyxtxt.estrattori.ocr_ollama import set_ollama_model, xtxt_image_describe

# Configure model (optional, default is gemma3:4b)
set_ollama_model("gemma3:12b")  # or llava:7b, llava:13b

# Extract only text (OCR mode)
text = xtxt("complex_document.png")

# Extract text + image description
description = xtxt_image_describe(open("diagram.png", "rb"))
# Output: "TEXT: Chart Title: Sales Report 2024\nDESCRIPTION: Bar chart showing quarterly sales data with blue bars"

# From web images
import requests
image_response = requests.get("https://example.com/document.png")
text = xtxt(image_response.content)
```

### Show Available Formats
```python
from pyxtxt import extxt_available_formats

# List supported MIME types
formats = extxt_available_formats()
print(formats)

# Pretty format names
formats = extxt_available_formats(pretty=True)
print(formats)
```
## 🌐 Common Web Use Cases

```python
# API responses
api_response = requests.post("https://api.example.com/generate-pdf")
text = xtxt(api_response.content)

# File uploads (Flask/Django)
uploaded_bytes = request.files['document'].read()
text = xtxt(uploaded_bytes)

# Audio/video transcription services
audio_response = requests.get("https://api.example.com/recording.mp3")
transcript = xtxt(audio_response.content)

# Video transcription from API
video_response = requests.get("https://api.example.com/meeting.mp4")
transcript = xtxt(video_response.content)

# OCR for uploaded images
image_bytes = request.files['receipt'].read()
text = xtxt(image_bytes)

# Email attachments
attachment_bytes = email_msg.get_payload(decode=True)
text = xtxt(attachment_bytes)
```

## ⚠️ Known Limitations

- **Legacy file detection**: When using raw streams without filenames, legacy files (.doc, .xls, .ppt) may not be correctly detected due to identical file signatures in libmagic
- **Filename hints recommended**: When available, providing original filenames improves detection accuracy
- **MSWrite .doc files**: Require `antiword` installation:
  ```bash
  sudo apt-get update && sudo apt-get install antiword
  ```

## 📖 Full Examples

### Accessing Examples After Installation
After installing PyxTxt from PyPI, you can access comprehensive usage examples including local file processing, memory buffer handling, web content extraction, error handling patterns, and all supported formats demonstration:

```python
import pkg_resources

# Get path to examples file
examples_path = pkg_resources.resource_filename('pyxtxt', 'examples.py')
print(f"Examples file location: {examples_path}")

# Run the examples directly
exec(open(examples_path).read())

# Or read the content to view examples
examples_content = pkg_resources.resource_string('pyxtxt', 'examples.py').decode('utf-8')
print(examples_content)
```

## 🔒 License

Distributed under the MIT License. See LICENSE file for details.

The software is provided "as is" without any warranty of any kind.

## 🤝 Contributing

Pull requests, issues, and feedback are warmly welcome! 🚀

- **Bug reports**: Please include file samples and error details
- **Feature requests**: Describe your use case and expected behavior
- **Code contributions**: Follow existing patterns and add tests

## 📊 Changelog

### v0.2.4
- ✅ **NEW**: Video transcription support (MP4, MOV, AVI, WebM, MKV)
- ✅ **ENHANCED**: Audio transcription now supports video files
- ✅ Whisper automatically extracts audio track from videos
- ✅ Unified interface for both audio and video processing

### v0.2.3
- ✅ **NEW**: Audio transcription support (MP3, WAV, M4A, FLAC, etc.)
- ✅ **NEW**: OCR from images (JPEG, PNG, TIFF, BMP, WebP)
- ✅ **NEW**: Markdown, EPUB, RTF, EML, MSG, LaTeX support
- ✅ Separate optional dependencies for heavy features (audio/OCR)
- ✅ Performance optimizations with model caching
- ✅ Improved multilingual OCR support (Italian/English)

### v0.1.24+
- ✅ Added support for `bytes` objects
- ✅ Added support for `requests.Response` objects  
- ✅ Added `xtxt_from_url()` helper function
- ✅ Improved type hints and error handling
- ✅ Enhanced web content processing capabilities
