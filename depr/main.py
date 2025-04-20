import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Import the cover letter generator
from depr.cover_letter_generator import CoverLetterGenerator

# Import the CV and JD modules directly
# Make sure these files are properly importable
sys.path.append('CV_Extractor')
sys.path.append('JD_Extractor')
from CV_Extractor.main_CV import main_CV
from JD_Extractor.main_JD import main_JD

def main():
    parser = argparse.ArgumentParser(description='End-to-end cover letter generation pipeline')
    parser.add_argument('--cv-path', type=str, required=True, help='Path to the CV PDF file')
    parser.add_argument('--jd-path', type=str, required=True, help='Path to the job description file')
    parser.add_argument('--output-dir', type=str, default='output', help='Directory to save output files')
    parser.add_argument('--api-key', type=str, help='OpenAI API key (optional if set as environment variable)')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Define paths for output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cv_json_path = output_dir / f"CV_extracted_{timestamp}.json"
    jd_json_path = output_dir / f"JD_extracted_{timestamp}.json"
    cover_letter_path = output_dir / f"Cover_Letter_{timestamp}.txt"
    
    # Step 1: Process CV directly
    print(f"Processing CV: {args.cv_path}")
    cv_success = main_CV(args.cv_path, str(cv_json_path))
    if not cv_success:
        print("CV processing failed. Exiting.")
        return
    print(f"CV processing completed. Output saved to: {cv_json_path}")
    
    # Step 2: Process Job Description
    print(f"Processing Job Description: {args.jd_path}")
    try:
        # Check if the input is a file path or a JSON file
        if os.path.isfile(args.jd_path) and args.jd_path.endswith('.json'):
            # If it's a JSON file, just copy it to the output directory
            with open(args.jd_path, 'r') as f:
                jd_data = json.load(f)
            with open(jd_json_path, 'w') as f:
                json.dump(jd_data, f, indent=4)
            print(f"Job description JSON copied to: {jd_json_path}")
        else:
            # If it's a text file or string, process it
            jd_extractor = main_JD(api_key=args.api_key)
            
            # Define the processing steps
            jd_processing_steps = [
                """Extract the core sections of the job description.
                Identify the job title, company name, location, summary, and key responsibilities.
                Separate different sections clearly and preserve the hierarchical structure.""",
                
                """From the identified sections, extract all requirements and qualifications.
                Distinguish between required qualifications (must-have) and preferred qualifications (nice-to-have).
                Include education requirements, years of experience, and necessary certifications.""",
                
                """Extract all skills mentioned in the job description.
                Categorize skills as technical skills, soft skills, and specific technologies/tools.
                Include programming languages, frameworks, methodologies, and other relevant technical knowledge.""",
                
                """Organize all extracted information into a structured format.
                Format the output as a hierarchical JSON object with clear section labels.
                Ensure all extracted information is categorized correctly under position details, responsibilities, qualifications, and skills."""
            ]
            
            # Get the job description text
            if os.path.isfile(args.jd_path):
                with open(args.jd_path, 'r') as file:
                    jd_text = file.read()
            else:
                jd_text = args.jd_path
            
            # Process the job description
            results = jd_extractor.process_job_description(jd_text, jd_processing_steps)
            
            # Save the formatted output
            jd_extractor.save_to_json(results["formatted_output"], filename=str(jd_json_path))
            print(f"Job description processing completed. Output saved to: {jd_json_path}")
    except Exception as e:
        print(f"Job description processing failed: {e}")
        return
    
    # Step 3: Generate Cover Letter
    print("Generating cover letter using GPT-4o...")
    try:
        # Initialize the generator with the same API key
        generator = CoverLetterGenerator(openai_api_key=args.api_key)
        
        # Load data from JSON files
        cv_data = generator.load_json_file(cv_json_path)
        job_data = generator.load_json_file(jd_json_path)
        
        # Generate the cover letter
        cover_letter = generator.generate_cover_letter(cv_data, job_data)
        
        if cover_letter:
            # Save the cover letter
            generator.save_cover_letter(cover_letter, cover_letter_path)
            print(f"Cover letter generation complete! Saved to: {cover_letter_path}")
        else:
            print("Failed to generate cover letter.")
            
    except Exception as e:
        print(f"Error in cover letter generation: {e}")
        return
    
    print("\nEntire pipeline completed successfully!")
    print(f"CV JSON: {cv_json_path}")
    print(f"JD JSON: {jd_json_path}")
    print(f"Cover Letter: {cover_letter_path}")

if __name__ == "__main__":
    main()