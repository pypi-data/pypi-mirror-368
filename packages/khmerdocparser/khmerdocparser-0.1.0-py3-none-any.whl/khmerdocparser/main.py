import argparse
import os
from PIL import Image
from pdf2image import convert_from_path
import easyocr
import sys

def extract_text_from_pdf(pdf_path, poppler_path=None):
    """
    Extracts Khmer and English text from a PDF file.

    This function converts each page of the specified PDF file into an image,
    then uses EasyOCR to extract Khmer and English text from each image.

    Args:
        pdf_path (str): The file path to the PDF.
        poppler_path (str, optional): The path to the Poppler binary folder.
                                      Required for Windows users if Poppler is not in PATH.

    Returns:
        str: The concatenated text extracted from all pages of the PDF.
             Returns an error message if the PDF file is not found.
    """
    if not os.path.exists(pdf_path):
        return f"Error: PDF file not found at '{pdf_path}'"

    print("Initializing OCR reader for Khmer and English...")
    # Initialize the OCR reader for Khmer and English languages
    reader = easyocr.Reader(['km', 'en'])
    
    full_text = ""
    
    try:
        print(f"Converting PDF '{os.path.basename(pdf_path)}' to images...")
        # Convert PDF to a list of PIL images
        images = convert_from_path(pdf_path, poppler_path=poppler_path)
        
        total_pages = len(images)
        print(f"Found {total_pages} page(s). Starting OCR process...")

        # Process each page
        for i, image in enumerate(images):
            print(f"  - Processing page {i + 1} of {total_pages}...")
            
            # Use the OCR reader to find text in the image
            result = reader.readtext(image, detail=0, paragraph=True)
            
            # Append the extracted text to the full text string
            page_text = "\n".join(result)
            full_text += page_text + f"\n\n--- Page {i + 1} ---\n\n"

        print("OCR process completed successfully.")

    except Exception as e:
        error_message = (
            f"An error occurred: {e}\n\n"
            "Please ensure you have installed the Poppler utility library for your "
            "operating system. See the README.md for installation instructions."
        )
        return error_message
        
    return full_text

def cli():
    """
    Command-line interface for the Khmer Document Parser tool.
    """
    parser = argparse.ArgumentParser(
        description="Extract Khmer text from a PDF file using OCR."
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

    # Add a version argument
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s 0.1.0"
    )

    args = parser.parse_args()

    # Check if pdf_file exists before proceeding
    if not os.path.isfile(args.pdf_file):
        print(f"Error: The file '{args.pdf_file}' does not exist.", file=sys.stderr)
        sys.exit(1)

    extracted_text = extract_text_from_pdf(args.pdf_file, args.poppler_path)
    
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(extracted_text)
            print(f"Successfully saved extracted text to '{args.output}'")
        except IOError as e:
            print(f"Error: Could not write to file '{args.output}'. Reason: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Print to standard output
        print(extracted_text)

if __name__ == "__main__":
    cli()