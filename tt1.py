import os
import re
import pdfplumber
from pdf2image import convert_from_path
import pytesseract

# Configure Tesseract OCR and Poppler paths (update paths as needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
poppler_path = r"C:\Program Files (x86)\poppler-24.08.0\Library\bin"
os.environ["PATH"] += os.pathsep + poppler_path

def extract_text_from_pdf(pdf_path, pages):
    """Extract text from PDF using pdfplumber."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num in pages:
                if page_num < len(pdf.pages):
                    page = pdf.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text

def extract_text_from_image(pdf_path, pages):
    """Extract text using OCR (pytesseract) from PDF images."""
    text = ""
    try:
        images = convert_from_path(pdf_path, first_page=pages[0]+1, last_page=pages[-1]+1, dpi=300)
        for i, image in enumerate(images):
            print(f"Performing OCR on page {pages[i]+1}...")
            page_text = pytesseract.image_to_string(image, lang="eng")
            text += page_text + "\n"
    except Exception as e:
        print(f"Error performing OCR: {e}")
    return text

def extract_unemployment_rate(text, degree_type="Bachelor"):
    """
    Extract the unemployment rate for a specific degree type.
    Default degree type is "Bachelor".
    """
    pattern = rf"{degree_type}.*?(\d+\.\d)%"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1)
    return None

def main():
    print("### PDF Degree-Based Unemployment Extractor ###")
    
    # Input: PDF file path
    pdf_path = input("Enter the path to the PDF file: ").strip()
    if not os.path.exists(pdf_path):
        print("Error: PDF file not found. Please provide a valid path.")
        return
    
    # Input: Pages to analyze
    pages_input = input("Enter the page numbers to analyze (comma-separated, e.g., 1,2): ").strip()
    try:
        pages = [int(p.strip()) - 1 for p in pages_input.split(",")]
    except ValueError:
        print("Error: Invalid page numbers. Please enter integers separated by commas.")
        return
    
    # Input: Degree type to extract unemployment rate
    degree_type = input("Enter the degree type to find (e.g., Bachelor, Doctoral): ").strip()

    print("\nExtracting text from PDF...")
    text = extract_text_from_pdf(pdf_path, pages)
    
    # If no text, use OCR fallback
    if not text.strip():
        print("No text found using pdfplumber. Switching to OCR...")
        text = extract_text_from_image(pdf_path, pages)
    
    if text.strip():
        print("\nSearching for unemployment rate...")
        rate = extract_unemployment_rate(text, degree_type)
        if rate:
            print(f"\nUnemployment Rate for '{degree_type}' Degree: {rate}%")
        else:
            print(f"Unemployment rate for '{degree_type}' degree not found in the extracted text.")
    else:
        print("Error: No text could be extracted from the given pages.")

if __name__ == "__main__":
    main()
