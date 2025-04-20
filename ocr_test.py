import os
import base64
import io
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
from pdf2image import convert_from_path
from IPython.display import display


import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
import fitz  # PyMuPDF

# Load environment variables
load_dotenv()
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
YOUR_SITE_URL = os.getenv('YOUR_SITE_URL', 'https://example.com')
YOUR_SITE_NAME = os.getenv('YOUR_SITE_NAME', 'PDF OCR Application')

# Initialize OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def convert_pdf_to_images(pdf_path, output_folder, dpi=300):
    """Convert PDF to images using PyMuPDF instead of pdf2image"""
    # Create output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    image_paths = []
    pdf_document = fitz.open(pdf_path)
    
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        
        # Set resolution (higher zoom = higher resolution)
        zoom_factor = dpi / 72  # 72 is the base DPI for PDF
        matrix = fitz.Matrix(zoom_factor, zoom_factor)
        
        # Render page to pixmap
        pixmap = page.get_pixmap(matrix=matrix)
        
        # Save image
        image_path = os.path.join(output_folder, f'page_{page_num+1}.jpg')
        pixmap.save(image_path)
        image_paths.append(image_path)
    
    pdf_document.close()
    return image_paths

def batch_images(image_paths, batch_size=10):
    """Group images into batches for processing"""
    for i in range(0, len(image_paths), batch_size):
        yield image_paths[i:i + batch_size]

def encode_image_to_base64(image_path):
    """Convert image to base64 encoded string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_images(image_paths, instruction):
    """Process images with Gemini 2.0 Flash through OpenRouter"""
    results = []
    
    for batch in batch_images(image_paths):
        # Prepare messages with multiple images
        message_content = [
            {
                "type": "text",
                "text": f"""
                {instruction}
                
                These are pages from a PDF document. Extract all text content while preserving the structure.
                Pay special attention to tables, columns, headers, and any structured content.
                Maintain paragraph breaks and formatting.
                """
            }
        ]
        
        # Add each image to the message content
        for img_path in batch:
            base64_image = encode_image_to_base64(img_path)
            message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })
        
        # Make the API call
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": YOUR_SITE_URL,
                "X-Title": YOUR_SITE_NAME,
            },
            model="google/gemini-2.0-flash-thinking-exp:free",
            messages=[
                {
                    "role": "user",
                    "content": message_content
                }
            ]
        )
        
        # Append the result
        results.append(completion.choices[0].message.content)
    
    # Combine all batch results
    return "\n\n".join(results)

def process_pdf(pdf_path, output_folder="./pdf_images", instruction=None):
    """Process a PDF document to extract text"""
    # Default instruction if not provided
    if instruction is None:
        instruction = "Extract all text from this document, including tables and formatting"
    
    print(f"Converting PDF: {pdf_path} to images...")
    image_paths = convert_pdf_to_images(pdf_path, output_folder)
    print(f"Converted {len(image_paths)} pages to images")
    
    print("Processing images with Gemini 2.0 Flash via OpenRouter...")
    result = process_images(image_paths, instruction)
    
    # Save the result to a file
    pdf_basename = os.path.splitext(os.path.basename(pdf_path))[0]
    output_file = f"./ocr_result/{pdf_basename}_extracted_text.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result)
    print(f"Extracted text saved to {output_file}")
    
    return result

# Example usage
if __name__ == "__main__":
    # Process a PDF
    pdf_path = "data/taxreturn.pdf"  # Your PDF path
    extracted_text = process_pdf(pdf_path)
    
    # Print a preview of the result
    print("\n===== EXTRACTED TEXT PREVIEW =====\n")
    print(extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text)