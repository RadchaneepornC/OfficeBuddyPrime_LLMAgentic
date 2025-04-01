import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


class JobDescriptionExtractor:
    def __init__(self, api_key=None):
        """
        Initialize the extractor with an OpenAI API key
        
        Args:
            api_key (str, optional): OpenAI API key. If not provided, will try to get from environment
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set as OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o"  
        self.debug = True  # Enable debug output

    def set_model(self, model_name):
        """Change the OpenAI model being used"""
        self.model = model_name

    def process_job_description(self, jd_text, processing_steps):
        """
        Process a job description through a chain of prompts
        
        Args:
            jd_text (str): The job description text
            processing_steps (list): List of processing instructions
            
        Returns:
            dict: Extracted and structured information from the JD
        """
        current_text = jd_text
        results = {}
        
        # Step 1: Extract key sections
        if len(processing_steps) >= 1:
            print("Step 1: Extracting key sections...")
            sections = self.extract_jd_sections(current_text, processing_steps[0])
            results["sections"] = sections
            current_text = sections  # Pass the structured sections to next step
        
        # Step 2: Extract requirements and qualifications
        if len(processing_steps) >= 2:
            print("Step 2: Extracting requirements and qualifications...")
            requirements = self.extract_requirements(current_text, processing_steps[1])
            results["requirements"] = requirements
            
        # Step 3: Extract skills and technologies
        if len(processing_steps) >= 3:
            print("Step 3: Extracting skills and technologies...")
            skills = self.extract_skills(current_text, processing_steps[2])
            results["skills"] = skills
            
        # Step 4: Format into structured output
        if len(processing_steps) >= 4:
            print("Step 4: Formatting structured output...")
            formatted_output = self.format_structured_output(results, processing_steps[3])
            results["formatted_output"] = formatted_output
        
        return results

    def extract_json_from_response(self, text):
        """
        Extract JSON from response text, handling various formats
        
        Args:
            text (str): The response text from the API
            
        Returns:
            dict: The extracted JSON object or None if extraction failed
        """
        # Debug output
        if self.debug:
            print("\nRaw response:")
            print(text[:200] + "..." if len(text) > 200 else text)
        
        # Method 1: Direct JSON parsing
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            if self.debug:
                print("Direct JSON parsing failed. Trying pattern matching...")
        
        # Method 2: Find JSON between triple backticks
        json_code_pattern = r"```(?:json)?\s*(\{[\s\S]*?\})\s*```"
        code_match = re.search(json_code_pattern, text, re.DOTALL)
        if code_match:
            try:
                return json.loads(code_match.group(1))
            except json.JSONDecodeError:
                if self.debug:
                    print("Code block JSON parsing failed. Trying broader pattern...")
        
        # Method 3: Find anything that looks like a JSON object
        json_pattern = r"(\{[\s\S]*?\})"
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                if self.debug:
                    print("Broad pattern JSON parsing failed. Cleaning and trying again...")
                
                # Method 4: Clean up the text and try one more time
                json_text = match.group(1)
                
                # Remove any stray backticks
                json_text = json_text.replace("`", "")
                
                # Fix common JSON syntax errors
                json_text = re.sub(r"(?<!\\\")(\w+)(?=\"\s*:)", r'"\1"', json_text)  # Add quotes to keys
                json_text = re.sub(r",\s*\}", "}", json_text)  # Remove trailing commas
                
                try:
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    if self.debug:
                        print("All JSON parsing methods failed.")
        
        # If all methods failed
        return None

    def extract_jd_sections(self, text, instructions):
        """
        Extract main sections from a job description using OpenAI GPT API
        
        Args:
            text (str): Job description text
            instructions (str): Instructions for extraction
            
        Returns:
            dict: Extracted sections (title, company, location, description, responsibilities)
        """
        # Construct the prompt
        prompt = f"""
        {instructions}
        
        Job Description:
        {text}
        
        Extract the following sections:
        - Job Title
        - Company Name
        - Location
        - Job Description Summary
        - Key Responsibilities
        
        IMPORTANT: Your entire response must be a valid JSON object with the following structure and nothing else:
        {{
            "job_title": "extracted job title",
            "company": "extracted company name",
            "location": "extracted location information",
            "summary": "extracted brief job summary",
            "responsibilities": ["responsibility 1", "responsibility 2", ...]
        }}
        
        Do not include any explanation, notes, or anything other than the JSON object itself.
        """
        
        # Make the API request
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured information from job descriptions and returns it as JSON. You only output valid JSON with no additional text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,  # Use 0 temperature for more consistent outputs
            response_format={"type": "json_object"},  # Request JSON output
            max_tokens=1500
        )
        
        # Extract the JSON response
        response_content = response.choices[0].message.content
        result = self.extract_json_from_response(response_content)
        
        if result:
            return result
        else:
            print("Warning: Could not parse JSON response from API")
            return {
                "job_title": "Error: Could not extract job title",
                "company": "Error: Could not extract company name",
                "location": "Error: Could not extract location",
                "summary": "Error: Could not extract summary",
                "responsibilities": ["Error: Could not extract responsibilities"]
            }

    def extract_requirements(self, sections, instructions):
        """
        Extract requirements and qualifications from job sections using OpenAI GPT API
        
        Args:
            sections (dict): Previously extracted job sections
            instructions (str): Instructions for extraction
            
        Returns:
            dict: Required and preferred qualifications
        """
        # Format the sections into a readable string
        sections_text = json.dumps(sections, indent=2)
        
        # Construct the prompt
        prompt = f"""
        {instructions}
        
        Previously extracted job sections:
        {sections_text}
        
        Extract and categorize the requirements and qualifications into:
        - Required qualifications (education, experience, certifications, etc.)
        - Preferred qualifications (nice-to-have)
        
        IMPORTANT: Your entire response must be a valid JSON object with the following structure and nothing else:
        {{
            "required_qualifications": ["requirement 1", "requirement 2", ...],
            "preferred_qualifications": ["preferred 1", "preferred 2", ...]
        }}
        
        Do not include any explanation, notes, or anything other than the JSON object itself.
        """
        
        # Make the API request
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts and categorizes job requirements and returns it as JSON. You only output valid JSON with no additional text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"},  # Request JSON output
            max_tokens=1500
        )
        
        # Extract the JSON response
        response_content = response.choices[0].message.content
        result = self.extract_json_from_response(response_content)
        
        if result:
            return result
        else:
            print("Warning: Could not parse JSON response from API")
            return {
                "required_qualifications": ["Error: Could not extract required qualifications"],
                "preferred_qualifications": ["Error: Could not extract preferred qualifications"]
            }

    def extract_skills(self, sections, instructions):
        """
        Extract technical skills, soft skills, and technologies from job sections using OpenAI GPT API
        
        Args:
            sections (dict): Previously extracted job sections
            instructions (str): Instructions for extraction
            
        Returns:
            dict: Technical skills, soft skills, and technologies
        """
        # Format the sections into a readable string
        sections_text = json.dumps(sections, indent=2)
        
        # Construct the prompt
        prompt = f"""
        {instructions}
        
        Previously extracted job sections:
        {sections_text}
        
        Extract and categorize all skills mentioned in the job description into:
        - Technical skills (programming languages, methodologies, etc.)
        - Soft skills (communication, teamwork, etc.)
        - Technologies (specific tools, platforms, frameworks, etc.)
        
        IMPORTANT: Your entire response must be a valid JSON object with the following structure and nothing else:
        {{
            "technical_skills": ["skill 1", "skill 2", ...],
            "soft_skills": ["skill 1", "skill 2", ...],
            "technologies": ["technology 1", "technology 2", ...]
        }}
        
        Do not include any explanation, notes, or anything other than the JSON object itself.
        """
        
        # Make the API request
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts and categorizes job skills and returns it as JSON. You only output valid JSON with no additional text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"},  # Request JSON output
            max_tokens=1500
        )
        
        # Extract the JSON response
        response_content = response.choices[0].message.content
        result = self.extract_json_from_response(response_content)
        
        if result:
            return result
        else:
            print("Warning: Could not parse JSON response from API")
            return {
                "technical_skills": ["Error: Could not extract technical skills"],
                "soft_skills": ["Error: Could not extract soft skills"],
                "technologies": ["Error: Could not extract technologies"]
            }

    def format_structured_output(self, results, instructions):
        """
        Format all extracted information into final structured output using OpenAI GPT API
        
        Args:
            results (dict): All previously extracted information
            instructions (str): Instructions for formatting
            
        Returns:
            dict: Final structured output
        """
        # Format the results into a readable string
        results_text = json.dumps(results, indent=2)
        
        # Construct the prompt
        prompt = f"""
        {instructions}
        
        Previously extracted information:
        {results_text}
        
        Format this information into a clean, organized structure following this schema:
        {{
            "position_details": {{
                "title": "job title",
                "company": "company name",
                "location": "location"
            }},
            "job_overview": "job summary",
            "responsibilities": ["responsibility 1", "responsibility 2", ...],
            "qualifications": {{
                "required": ["required qualification 1", "required qualification 2", ...],
                "preferred": ["preferred qualification 1", "preferred qualification 2", ...]
            }},
            "skills_required": {{
                "technical": ["technical skill 1", "technical skill 2", ...],
                "soft": ["soft skill 1", "soft skill 2", ...],
                "technologies": ["technology 1", "technology 2", ...]
            }}
        }}
        
        IMPORTANT: Your entire response must be a valid JSON object with the structure shown above and nothing else.
        Do not include any explanation, notes, or anything other than the JSON object itself.
        """
        
        # Make the API request
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that formats structured job information and returns it as JSON. You only output valid JSON with no additional text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"},  # Request JSON output
            max_tokens=1500
        )
        
        # Extract the JSON response
        response_content = response.choices[0].message.content
        result = self.extract_json_from_response(response_content)
        
        if result:
            return result
        else:
            print("Warning: Could not parse JSON response from API")
            # Create a simplified structure with error messages
            return {
                "position_details": {
                    "title": "Error: Could not format output",
                    "company": "Error: Could not format output",
                    "location": "Error: Could not format output"
                },
                "job_overview": "Error: Could not format output",
                "responsibilities": ["Error: Could not format output"],
                "qualifications": {
                    "required": ["Error: Could not format output"],
                    "preferred": ["Error: Could not format output"]
                },
                "skills_required": {
                    "technical": ["Error: Could not format output"],
                    "soft": ["Error: Could not format output"],
                    "technologies": ["Error: Could not format output"]
                }
            }
    
    def save_to_json(self, data, filename="job_description_scb1.json"):
        """
        Save the structured job description to a JSON file
        
        Args:
            data (dict): The structured job description data
            filename (str): Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Results saved to {filename}")
        except Exception as e:
            print(f"Error saving results to file: {str(e)}")

# Main function to run the JD extraction process
def main():
    try:
        # Initialize the extractor
        extractor = JobDescriptionExtractor()
        
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
        
        # Get the job description
        jd_text = """About the job
Who is Sertis?

At Sertis, we stand at the forefront of technological innovation, harnessing the power of cutting-edge AI and data solutions to drive unparalleled business value for enterprises. Our AI and data centric solutions empower businesses, fostering adaptability in the face of change and transforming potential challenges into lucrative opportunities.

Our focus extends across Retail and FMCG industries as well as Energy, Security, and Asset Management. In the future, our expertise will expand to include Financial Services and Telco. We offer comprehensive AI and data science, data infrastructure, data visualization, and software engineering products and services that empower our clients to navigate the complex landscape of the modern business world.

Overview of the job

We are seeking a passionate and skilled Senior LLM Data Scientist to enhance our team's capabilities in designing and implementing LLM based solutions. This role involves active participation in solution design, model implementation and testing as well as making sure to keep up to date with the latest cutting edge GenAI technologies. Collaborate with a diverse team to design and implement AI models that address complex business challenges.

In this role, you will get to:

Contribute to a range of projects including but not limited to chatbot, RAG system or custom SLM
Engage in rigorous testing and validation of AI models to ensure efficiency, reliability and accuracy.
Utilize a variety of cloud platforms (AWS, Azure, Google Cloud) for the development and deployment of solutions.
Ensure continuous improvement and upkeep of models by leveraging the latest in AI research and methodologies.

You’ll be successful if you have:

Proven experience in Python and familiarity with libraries such as PyTorch, scikit-learn, Pandas, langchain
Proven experience in designing and implementing RAG system, tuning custom SLM or any other LLM based solution
Experience with Ubuntu and other Linux distributions.
Strong understanding of AI and data science, with an emphasis on latest GenAI technology
Excellent problem-solving skills and the ability to work collaboratively in a team.
Bachelor’s or Master’s degree in Computer Science, Data Science, Artificial Intelligence, or a related field.
Strong background in developing solutions on cloud platforms like AWS, Azure, and Google Cloud is a plus

What are some benefits working at Sertis? 

The opportunity to work with a dynamic team that is at the forefront of AI technology.
An hybrid work environment with 3 days or remote work per week
A culture that is collaborative, innovative, and supportive.
Competitive salary and benefits package.
Professional development opportunities and career advancement.

We are excited to see how you can contribute to our team's success and help shape the future of AI!

Sertis may collect, use, or disclose your personal data or personal data of other persons provided by you in order to carry out your recruitment process. For more information, please refer to our Recruitment Privacy Notice"""
        
        # Check if the input is a file path
        if os.path.isfile(jd_text):
            with open(jd_text, 'r') as file:
                jd_text = file.read()
        
        # Process the job description
        print("Processing job description...")
        results = extractor.process_job_description(jd_text, jd_processing_steps)
        
        # Output the results
        print("\nStructured Job Description:")
        print(json.dumps(results["formatted_output"], indent=2))

        extractor.save_to_json(results["formatted_output"])
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


# Example usage
if __name__ == "__main__":
    main()