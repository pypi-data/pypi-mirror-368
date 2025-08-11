# Khmer Document Parser

`khmerdocparser` is a command-line tool to extract Khmer text from PDF files. It works by converting each page of a PDF into an image and then using optical character recognition (OCR) to extract the text.

This tool uses the powerful [EasyOCR](https://github.com/JaidedAI/EasyOCR) library.

## Features

- Extracts both Khmer and English text from PDFs.
- Simple command-line interface.
- Option to save extracted text to a file.
- Can be used as a library in your own Python projects.

## Prerequisites

This package requires a crucial external dependency called **Poppler**. You must install it on your system before using this tool.

### Poppler Installation

- **Windows**:
  1. Download the latest Poppler binary for Windows from [here](https://github.com/oschwartz10612/poppler-windows/releases/).
  2. Extract the archive (e.g., to `C:\Program Files\poppler-23.11.0`).
  3. Add the `bin` directory inside the extracted folder (e.g., `C:\Program Files\poppler-23.11.0\bin`) to your system's PATH environment variable.
  4. Alternatively, you can use the `--poppler_path` argument when running the script to point to this `bin` directory.

- **macOS (using Homebrew)**:
  ```bash
  brew install poppler
  ```

- **Linux (Debian/Ubuntu)**:
  ```bash
  sudo apt-get update
  sudo apt-get install poppler-utils
  ```

## Installation

Once Poppler is installed, you can install this package from PyPI:

```bash
pip install khmerdocparser
```

## Usage

### As a Command-Line Tool

To extract text from a PDF and print it to the console:
```bash
khmerdocparser /path/to/your/document.pdf
```

To save the extracted text to a file:
```bash
khmerdocparser /path/to/your/document.pdf --output extracted_text.txt
```

If you are on Windows and did not add Poppler to your PATH:
```bash
khmerdocparser C:\Users\You\doc.pdf --poppler_path "C:\path\to\poppler\bin"
```

### As a Python Library

You can also import and use the function directly in your code.

```python
from khmerdocparser.main import extract_text_from_pdf

pdf_path = "/path/to/your/document.pdf"

# For Windows, if Poppler is not in PATH
# poppler_bin_path = "C:\path\to\poppler\bin"
# text = extract_text_from_pdf(pdf_path, poppler_path=poppler_bin_path)

# For macOS and Linux
text = extract_text_from_pdf(pdf_path)

print(text)
```

## How to Publish (for Developers)

1.  **Build the package**:
    ```bash
    pip install build twine
    python -m build
    ```

2.  **Upload to PyPI**:
    ```bash
    twine upload dist/*
    ```
    You will need a PyPI account and an API token for this step.