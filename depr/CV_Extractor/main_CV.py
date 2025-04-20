import os
import sys
import json
import re
import argparse
from datetime import datetime
import PyPDF2

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file using PyPDF2
    """
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

def basic_cv_structure(text):
    """
    Create a basic structure for CV data using regex patterns to identify sections
    This is a simplified approach - production systems would use more sophisticated NLP
    """
    cv_data = {
        "raw_text": text,
        "sections": {},
        "contact_info": {},
        "extracted_at": datetime.now().isoformat()
    }
    
    # Basic pattern matching for common CV sections
    sections = {
        "education": r"(?i)education|academic|qualification|degree",
        "experience": r"(?i)experience|employment|work history|professional experience",
        "skills": r"(?i)skills|expertise|proficiency|technical skills",
        "projects": r"(?i)projects|portfolio|works",
        "certifications": r"(?i)certifications|certificates|accreditation",
        "languages": r"(?i)languages|language proficiency",
    }
    
    # Extract email and phone using regex
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    phone_pattern = r'(\+\d{1,3}[-\s]?)?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}'
    
    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)
    
    if emails:
        cv_data["contact_info"]["email"] = emails[0]
    if phones:
        cv_data["contact_info"]["phone"] = phones[0]
    
    # Split the document into lines
    lines = text.split('\n')
    
    # Try to identify a name from the first few lines (simple heuristic)
    for i in range(min(5, len(lines))):
        if lines[i].strip() and not re.search(r'@|www|\d{3}', lines[i]):
            cv_data["contact_info"]["name"] = lines[i].strip()
            break
    
    # Attempt to identify sections in the document
    current_section = None
    section_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if this line is a section header
        for section_name, pattern in sections.items():
            if re.search(pattern, line, re.IGNORECASE) and len(line) < 50:  # Assuming headers are short
                # If we were building a previous section, save it
                if current_section:
                    cv_data["sections"][current_section] = "\n".join(section_content)
                
                # Start a new section
                current_section = section_name
                section_content = []
                break
        else:
            # If this is not a header and we're in a section, add to current section
            if current_section:
                section_content.append(line)
    
    # Add the last section if there is one
    if current_section and section_content:
        cv_data["sections"][current_section] = "\n".join(section_content)
    
    return cv_data

def save_to_json(data, output_path):
    """
    Save the extracted data to a JSON file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        print(f"Data successfully saved to {output_path}")
        return True
    except Exception as e:
        print(f"Error saving to JSON: {e}")
        return False

def process_cv(pdf_path, output_path=None):
    """
    Process a CV from PDF to JSON
    """
    # Validate the PDF path
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return False
    
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print("Failed to extract text from the PDF")
        return False
    
    # Structure the CV data
    cv_data = basic_cv_structure(text)
    
    # Determine output path if not provided
    if not output_path:
        filename = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = f"{filename}_extracted.json"
    
    # Save to JSON
    return save_to_json(cv_data, output_path)

def main_CV():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Extract CV data from PDF to JSON')
    parser.add_argument('pdf_path', help='Path to the PDF file')
    parser.add_argument('-o', '--output', help='Output JSON file path')
    
    args = parser.parse_args()
    
    # Process the CV
    success = process_cv(args.pdf_path, args.output)
    
    if success:
        print("CV processing completed successfully!")
    else:
        print("CV processing failed")
        sys.exit(1)

if __name__ == "__main__":
    main_CV()