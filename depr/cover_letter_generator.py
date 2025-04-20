import json
import os
import sys
import argparse
from pathlib import Path
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CoverLetterGenerator:
    def __init__(self, openai_api_key=None):
        """Initialize the Cover Letter Generator with API key"""
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable or provide it directly.")
        
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def load_json_file(self, file_path):
        """Load and parse a JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading JSON file {file_path}: {e}")
            sys.exit(1)
    
    def generate_cover_letter(self, cv_data, job_data):
        """Generate a cover letter using GPT-4o based on CV and JD data"""
        
        # Create system prompt for optimal cover letter generation
        system_prompt = """
        You are an expert cover letter writer with deep knowledge of recruiting and hiring practices.
        Your task is to create a compelling, tailored cover letter that positions the candidate as an ideal match for the specific job.
        
        Guidelines:
        1. Analyze both the job description and candidate's CV to identify key matching skills and qualifications
        2. Highlight the most relevant experiences and achievements that make the candidate well-suited for this role
        3. Address any potential gaps by emphasizing transferable skills
        4. Use a professional but engaging tone that reflects the industry standards
        5. Keep the letter concise (300-400 words) but comprehensive
        6. Structure the letter with proper introduction, body paragraphs highlighting qualifications, and strong closing
        7. Avoid generic language - be specific about how the candidate's background relates to the job requirements
        8. Personalize the letter to the company where possible
        9. Format the letter professionally with proper date, greeting, and signature
        
        The goal is to create a cover letter that clearly demonstrates why this specific candidate is an excellent fit for this specific position.
        """
        
        # Create user message with structured CV and job data
        user_message = f"""
        Please create a tailored cover letter based on the following:
        
        ## JOB DETAILS:
        {json.dumps(job_data, indent=2)}
        
        ## CANDIDATE CV:
        {json.dumps(cv_data, indent=2)}
        
        Generate a professional cover letter that highlights how this candidate's qualifications match the job requirements.
        """
        
        # Call GPT-4o API
        try:
            payload = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.7,
                "max_tokens": 1500
            }
            
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            cover_letter = result["choices"][0]["message"]["content"]
            return cover_letter
        
        except Exception as e:
            print(f"Error generating cover letter: {e}")
            if 'response' in locals() and hasattr(response, 'text'):
                print(f"API response: {response.text}")
            return None
    
    def save_cover_letter(self, cover_letter, output_path):
        """Save the generated cover letter to a file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(cover_letter)
            print(f"Cover letter saved to {output_path}")
        except Exception as e:
            print(f"Error saving cover letter: {e}")


def main():
    parser = argparse.ArgumentParser(description='Generate a cover letter using GPT-4o based on CV and job description data')
    parser.add_argument('--cv-json', type=str, required=True, help='Path to the CV JSON file')
    parser.add_argument('--jd-json', type=str, required=True, help='Path to the job description JSON file')
    parser.add_argument('--output', type=str, default='generated_cover_letter.txt', help='Output file path for the cover letter')
    parser.add_argument('--api-key', type=str, help='OpenAI API key (optional if set as environment variable)')
    
    args = parser.parse_args()
    
    # Initialize the generator
    generator = CoverLetterGenerator(args.api_key)
    
    # Load data from JSON files
    cv_data = generator.load_json_file(args.cv_json)
    job_data = generator.load_json_file(args.jd_json)
    
    # Generate the cover letter
    print("Generating cover letter...")
    cover_letter = generator.generate_cover_letter(cv_data, job_data)
    
    if cover_letter:
        # Save the cover letter
        generator.save_cover_letter(cover_letter, args.output)
    else:
        print("Failed to generate cover letter.")


if __name__ == "__main__":
    main()