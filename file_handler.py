import os
import mimetypes
import pymupdf
#import fitz  # PyMuPDF
import pdfplumber
from PIL import Image
import pytesseract
import json
import io

def detect_file_type(file_path):
    # Detect the MIME type using mimetypes library
    mime_type, _ = mimetypes.guess_type(file_path)
    
    # Check for plain text files
    if mime_type == 'text/plain':
        return "Plain Text"
    
    # Check for PDF files
    elif mime_type == 'application/pdf':
        try:
            # Check if the PDF has text content using PyMuPDF
            with pymupdf.open(file_path) as pdf:
                for page_num in range(pdf.page_count):
                    page = pdf.load_page(page_num)
                    text = page.get_text("text")
                    if text.strip():  # if there's any text content
                        return "Digital PDF"
            
            # If no text was found, apply OCR to determine if it's a scanned PDF
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    image = page.to_image()
                    text = pytesseract.image_to_string(image.original)
                    if text.strip():  # if OCR finds text
                        return "Scanned PDF"
            
            # If no text is detected, classify as unknown PDF type
            return "Unknown PDF"

        except Exception as e:
            return f"Error processing PDF: {e}"
    
    # Check for image files
    elif mime_type and mime_type.startswith('image'):
        try:
            with Image.open(file_path) as img:
                text = pytesseract.image_to_string(img)
                if text.strip():  # if OCR finds text
                    return "Image with Text"
                else:
                    return "Image without Text"
        except Exception as e:
            return f"Error processing Image: {e}"
    
    # If MIME type doesn't match any known types, return unknown
    else:
        return "Unknown File Type"

# assume pdf is digital pdf. Create an array index as page number and value as the text 
def extract_text_from_digital_pdf(pdf_path):
    """Extracts text, images, and tables from each page of a digital PDF."""
    extracted_content = {}

    # Open the PDF using PyMuPDF for text and image extraction
    with pymupdf.open(pdf_path) as pdf:
        # Open the PDF with pdfplumber for table extraction
        with pdfplumber.open(pdf_path) as pdf_plumber:
            for page_num in range(pdf.page_count):
                page_content = {
                    "text": "",
                    "tables": [],
                    "images": []
                }

                # Extract text using PyMuPDF
                page = pdf[page_num]
                page_content["text"] = page.get_text("text")

                # Extract tables using pdfplumber
                plumber_page = pdf_plumber.pages[page_num]
                table = plumber_page.extract_table()
                if table:
                    page_content["tables"] = table

                # Extract images using PyMuPDF
                image_list = page.get_images(full=True)
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = pdf.extract_image(xref)
                    image_bytes = base_image["image"]
                    image = Image.open(io.BytesIO(image_bytes))
                    width, height = image.size
                    rect = page.get_image_rects(xref)[0]  # Get bounding box
                    # Apply OCR to image if needed
                    image_text = pytesseract.image_to_string(image)
                    page_content["images"].append({
                        "image_index": img_index,
                        "image_data": image,
                        "ocr_text": image_text,
                        "width": width,
                        "height": height,
                        "bounding_box": {
                            "x0": rect.x0,
                            "y0": rect.y0,
                            "x1": rect.x1,
                            "y1": rect.y1
                        }
                    })

                # Store the extracted content for each page
                extracted_content[page_num + 1] = page_content

    return extracted_content

# save the extracted content to a directory
# If output directory is already created, then the content will be overwritten
# save the text to a txt file for each page
# save the tables to a csv file for each page
# save the images to a png file for each page

def save_pdf_content_to_dir(pdf_path, output_dir):
    """
    Save extracted PDF content to a directory structure.
    Creates separate folders for text, tables, and images.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'text'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'tables'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)

    # Extract content from PDF
    extracted_content = extract_text_from_digital_pdf(pdf_path)

 # Initialize a list to store all image metadata
    all_image_metadata = []
    
    # Process each page
    for page_num, page_content in extracted_content.items():
        # Save text content
        text_path = os.path.join(output_dir, 'text', f'page_{page_num}.txt')
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(page_content["text"])

        # Save tables if they exist
        if page_content["tables"]:
            import csv
            table_path = os.path.join(output_dir, 'tables', f'page_{page_num}.csv')
            with open(table_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(page_content["tables"])

        # Save images if they exist
        for img_data in page_content["images"]:
            img_index = img_data["image_index"]
            image = img_data["image_data"]
            image_path = os.path.join(output_dir, 'images', f'page_{page_num}_image_{img_index}.png')
            image.save(image_path, 'PNG')

           # Create metadata dictionary including OCR text and image info
            image_metadata = {
                "page_number": page_num,
                "image_path": image_path,
                "image_index": img_index,
                "width": img_data["width"],
                "height": img_data["height"],
                "bounding_box": img_data["bounding_box"],
                "ocr_text": img_data["ocr_text"]
            }
            all_image_metadata.append(image_metadata)

    # Save all image metadata in a single JSON file
    if all_image_metadata:
        metadata_path = os.path.join(output_dir, 'images', 'pdf_images_metadata.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(all_image_metadata, f, indent=4)



    return output_dir