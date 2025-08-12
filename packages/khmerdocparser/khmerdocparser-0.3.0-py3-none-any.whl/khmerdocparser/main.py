import argparse
import os
import sys
import logging
import cv2
import numpy as np
import pytesseract
import pdfplumber
from pdf2image import convert_from_path
from PIL import Image
from tqdm import tqdm

# --- Setup Logging ---
def setup_logging():
    """Configures logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("khmerdocparser.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

# --- Image Processing ---
def preprocess_image_for_ocr(image):
    """Applies preprocessing to an image to improve OCR accuracy."""
    open_cv_image = np.array(image)
    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY if len(open_cv_image.shape) == 3 else cv2.COLOR_RGB2GRAY)
    binary_image = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    denoised_image = cv2.medianBlur(binary_image, 3)
    return denoised_image

def extract_text_from_image_file(image_path: str, tesseract_cmd: str = None) -> str:
    """Extracts text from a single image file."""
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    logging.info(f"Processing image file: {image_path}")
    try:
        image = Image.open(image_path)
        preprocessed_image = preprocess_image_for_ocr(image)
        text = pytesseract.image_to_string(preprocessed_image, lang='khm+eng')
        logging.info("Successfully extracted text from image.")
        return text
    except Exception as e:
        logging.error(f"Failed to process image file '{image_path}'. Reason: {e}")
        return ""

# --- PDF Processing ---
def parse_scanned_pdf(pdf_path, poppler_path=None, tesseract_cmd=None):
    """Extracts text from a scanned (image-based) PDF using OCR."""
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    full_text = ""
    images = convert_from_path(pdf_path, poppler_path=poppler_path, dpi=300)
    
    for i, image in enumerate(tqdm(images, desc="Performing OCR on PDF pages")):
        logging.info(f"  - Preprocessing and reading page {i + 1}...")
        preprocessed_image = preprocess_image_for_ocr(image)
        page_text = pytesseract.image_to_string(preprocessed_image, lang='khm+eng')
        full_text += page_text + f"\n\n--- Page {i + 1} ---\n\n"
    return full_text

def parse_native_pdf(pdf_path: str) -> str:
    """Extracts text directly from a native (text-based) PDF."""
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in tqdm(pdf.pages, desc="Extracting text from native PDF"):
            text = page.extract_text()
            if text:
                full_text += text + f"\n\n--- Page {page.page_number} ---\n\n"
    return full_text

def process_pdf(pdf_path, poppler_path=None, tesseract_cmd=None):
    """
    Smartly processes a PDF by first trying direct text extraction,
    then falling back to OCR if necessary.
    """
    logging.info(f"Processing PDF file: {pdf_path}")
    try:
        # Try native text extraction first
        logging.info("Attempting direct text extraction (for native PDFs)...")
        native_text = parse_native_pdf(pdf_path)
        # If we get meaningful text, return it.
        if native_text and len(native_text.strip()) > 5: # Simple check for content
            logging.info("Successfully extracted text from native PDF.")
            return native_text
    except Exception as e:
        logging.warning(f"Direct text extraction failed: {e}. This may be a scanned PDF.")

    # Fallback to OCR for scanned PDFs or if native extraction fails
    logging.info("Falling back to OCR for scanned PDF processing...")
    try:
        scanned_text = parse_scanned_pdf(pdf_path, poppler_path, tesseract_cmd)
        logging.info("Successfully extracted text using OCR.")
        return scanned_text
    except Exception as e:
        logging.error(f"OCR processing failed. Reason: {e}")
        return ""

# --- Command-Line Interface ---
def cli():
    """Command-line interface for the Khmer Document Parser tool."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="A smart tool to extract Khmer text from PDF and image files."
    )
    parser.add_argument(
        "input_file", 
        type=str, 
        help="The path to the PDF or image file to process."
    )
    parser.add_argument(
        "--output", "-o", type=str,
        help="Optional: The path to the output .txt file."
    )
    parser.add_argument(
        "--poppler_path", type=str,
        help="Optional for Windows: The path to the Poppler 'bin' directory."
    )
    parser.add_argument(
        "--tesseract_path", type=str,
        help="Optional: The full path to the Tesseract executable."
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version=f"%(prog)s 0.3.0"
    )

    args = parser.parse_args()
    input_path = args.input_file

    if not os.path.isfile(input_path):
        logging.error(f"Error: The file '{input_path}' does not exist.")
        sys.exit(1)

    file_extension = os.path.splitext(input_path)[1].lower()
    extracted_text = ""

    if file_extension == '.pdf':
        extracted_text = process_pdf(input_path, args.poppler_path, args.tesseract_path)
    elif file_extension in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']:
        extracted_text = extract_text_from_image_file(input_path, args.tesseract_path)
    else:
        logging.error(f"Unsupported file type: '{file_extension}'. Please provide a PDF or image file.")
        sys.exit(1)
    
    if not extracted_text.strip():
        logging.warning("Extraction resulted in no text.")
        return

    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(extracted_text)
            logging.info(f"Successfully saved extracted text to '{args.output}'")
        except IOError as e:
            logging.error(f"Could not write to file '{args.output}'. Reason: {e}")
            sys.exit(1)
    else:
        # Print to standard output, ensuring terminal can handle it
        try:
            print(extracted_text)
        except UnicodeEncodeError:
            logging.warning("Could not print Khmer text to the terminal due to encoding issues.")
            logging.info("Suggestion: Use the --output flag to save results to a text file.")

if __name__ == "__main__":
    cli()