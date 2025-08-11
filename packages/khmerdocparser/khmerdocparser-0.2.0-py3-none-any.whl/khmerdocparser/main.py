import argparse
import os
import sys
import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

def extract_text_from_pdf(pdf_path, poppler_path=None, tesseract_cmd=None):
    """
    Extracts Khmer and English text from a PDF file using Tesseract OCR.

    This function converts each page of the PDF into an image, then uses
    Tesseract to extract Khmer and English text.

    Args:
        pdf_path (str): The file path to the PDF.
        poppler_path (str, optional): The path to the Poppler binary folder.
        tesseract_cmd (str, optional): The path to the Tesseract executable.

    Returns:
        str: The concatenated text extracted from all pages.
    """
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    if not os.path.exists(pdf_path):
        return f"Error: PDF file not found at '{pdf_path}'"

    full_text = ""
    
    try:
        print(f"Converting PDF '{os.path.basename(pdf_path)}' to images...")
        images = convert_from_path(pdf_path, poppler_path=poppler_path)
        
        total_pages = len(images)
        print(f"Found {total_pages} page(s). Starting Tesseract OCR process...")

        for i, image in enumerate(images):
            print(f"  - Processing page {i + 1} of {total_pages}...")
            
            # Convert PIL image to OpenCV format (NumPy array)
            open_cv_image = np.array(image)
            # Convert RGB to BGR
            open_cv_image = open_cv_image[:, :, ::-1].copy()

            # Use Tesseract to find Khmer and English text
            # Tesseract uses 'khm' for Khmer
            page_text = pytesseract.image_to_string(open_cv_image, lang='khm+eng')
            
            full_text += page_text + f"\n\n--- Page {i + 1} ---\n\n"

        print("OCR process completed successfully.")

    except pytesseract.TesseractNotFoundError:
        return (
            "Tesseract Error: The Tesseract executable was not found.\n"
            "Please make sure you have installed Tesseract OCR on your system "
            "and that it's in your system's PATH. Alternatively, you can specify "
            "the path using the --tesseract_path argument.\n"
            "See the README.md for installation instructions."
        )
    except Exception as e:
        return (
            f"An unexpected error occurred: {e}\n\n"
            "Please ensure you have installed all required libraries and external "
            "dependencies like Poppler and Tesseract OCR. See the README.md for details."
        )
        
    return full_text

def cli():
    """
    Command-line interface for the Khmer Document Parser tool.
    """
    parser = argparse.ArgumentParser(
        description="Extract Khmer text from a PDF file using Tesseract OCR."
    )
    parser.add_argument(
        "pdf_file", 
        type=str, 
        help="The path to the PDF file to process."
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Optional: The path to the output text file to save the results."
    )
    parser.add_argument(
        "--poppler_path",
        type=str,
        help="Optional for Windows: The path to the Poppler 'bin' directory."
    )
    parser.add_argument(
        "--tesseract_path",
        type=str,
        help="Optional: The full path to the Tesseract executable (e.g., C:\...\tesseract.exe)."
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s 0.2.0"
    )

    args = parser.parse_args()

    if not os.path.isfile(args.pdf_file):
        print(f"Error: The file '{args.pdf_file}' does not exist.", file=sys.stderr)
        sys.exit(1)

    extracted_text = extract_text_from_pdf(args.pdf_file, args.poppler_path, args.tesseract_path)
    
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(extracted_text)
            print(f"Successfully saved extracted text to '{args.output}'")
        except IOError as e:
            print(f"Error: Could not write to file '{args.output}'. Reason: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(extracted_text)

if __name__ == "__main__":
    cli()