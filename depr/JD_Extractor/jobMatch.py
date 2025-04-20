# def generate_job_match_score(self, jd_structured, candidate_profile, instructions):
    #     """
    #     Optional: Generate a job match score between a job description and candidate profile
        
    #     Args:
    #         jd_structured (dict): Structured job description
    #         candidate_profile (dict): Candidate profile information
    #         instructions (str): Instructions for matching
            
    #     Returns:
    #         dict: Match score and analysis
    #     """
    #     # Format the inputs into readable strings
    #     jd_text = json.dumps(jd_structured, indent=2)
    #     profile_text = json.dumps(candidate_profile, indent=2)
        
    #     # Construct the prompt
    #     prompt = f"""
    #     {instructions}
        
    #     Job Description:
    #     {jd_text}
        
    #     Candidate Profile:
    #     {profile_text}
        
    #     Compare the job requirements against the candidate profile.
    #     For each requirement and skill:
    #     - Score exact matches as 1.0
    #     - Score partial/related matches as 0.5
    #     - Score missing requirements as 0.0
        
    #     Return a match analysis in JSON format with the following structure:
    #     {{
    #         "overall_match_score": 0.0-1.0,
    #         "match_breakdown": {{
    #             "skills": 0.0-1.0,
    #             "experience": 0.0-1.0,
    #             "education": 0.0-1.0
    #         }},
    #         "strengths": ["strength 1", "strength 2", ...],
    #         "gaps": ["gap 1", "gap 2", ...]
    #     }}
    #     """
        
    #     # Make the API request
    #     response = self.client.chat.completions.create(
    #         model=self.model,
    #         messages=[
    #             {"role": "system", "content": "You are a helpful assistant that assesses job match scores for candidates."},
    #             {"role": "user", "content": prompt}
    #         ],
    #         temperature=0.2,
    #         max_tokens=1000
    #     )
        
    #     # Extract the JSON response
    #     try:
    #         result = json.loads(response.choices[0].message.content)
    #         return result
    #     except json.JSONDecodeError:
    #         print("Warning: Could not parse JSON response from API")
    #         return {
    #             "overall_match_score": 0.0,
    #             "match_breakdown": {
    #                 "skills": 0.0,
    #                 "experience": 0.0,
    #                 "education": 0.0
    #             },
    #             "strengths": ["Error: Could not analyze match"],
    #             "gaps": ["Error: Could not analyze match"]
    #         }