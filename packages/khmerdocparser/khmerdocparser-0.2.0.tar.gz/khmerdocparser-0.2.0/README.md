# Khmer Document Parser v0.2.0

`khmerdocparser` is a command-line tool to extract Khmer text from PDF files. It works by converting each page of a PDF into an image and then using Google's Tesseract OCR engine to extract the text.

This tool uses the [Pytesseract](https://github.com/madmaze/pytesseract) library as a wrapper for Tesseract.

## Features

- Extracts both Khmer and English text from PDFs using Tesseract.
- Simple command-line interface.
- Option to save extracted text to a file.
- Can be used as a library in your own Python projects.

## Prerequisites

This package requires **two** crucial external dependencies: **Poppler** (for handling PDFs) and **Tesseract OCR** (for recognizing text). You must install both on your system.

### 1. Tesseract OCR Installation

You must install the Tesseract engine and the Khmer language pack.

- **Windows**:
  1. Download and run the Tesseract installer from [UB-Mannheim's GitHub](https://github.com/UB-Mannheim/tesseract/wiki).
  2. During installation, make sure to check the box for the **Khmer** language pack to include it.
  3. **Important**: Add the Tesseract installation directory (e.g., `C:\Program Files\Tesseract-OCR`) to your system's `PATH` environment variable.

- **macOS (using Homebrew)**:
  ```bash
  # Install Tesseract engine
  brew install tesseract

  # Install all available language packs, including Khmer
  brew install tesseract-lang
  ```

- **Linux (Debian/Ubuntu)**:
  ```bash
  # Install Tesseract engine
  sudo apt-get update
  sudo apt-get install tesseract-ocr

  # Install the Khmer language pack
  sudo apt-get install tesseract-ocr-khm
  ```

### 2. Poppler Installation

- **Windows**:
  1. Download the latest Poppler binary from [here](https://github.com/oschwartz10612/poppler-windows/releases/).
  2. Extract the archive and add its `bin` directory to your system's `PATH`.

- **macOS (using Homebrew)**:
  ```bash
  brew install poppler
  ```

- **Linux (Debian/Ubuntu)**:
  ```bash
  sudo apt-get install poppler-utils
  ```

## Installation

Once Poppler and Tesseract are installed, you can install this package from PyPI:

```bash
pip install --upgrade khmerdocparser
```

## Usage

### As a Command-Line Tool

To extract text and print it to the console:
```bash
khmerdocparser /path/to/your/document.pdf
```

To save the extracted text to a file:
```bash
khmerdocparser /path/to/your/document.pdf -o extracted_text.txt
```

If Tesseract or Poppler are not in your system's PATH, you can specify their locations:
```bash
khmerdocparser doc.pdf --tesseract_path "C:\Tesseract\tesseract.exe" --poppler_path "C:\Poppler\bin"
```

### As a Python Library

```python
from khmerdocparser.main import extract_text_from_pdf

pdf_path = "/path/to/your/document.pdf"
text = extract_text_from_pdf(pdf_path)
print(text)
```