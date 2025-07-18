# https://docs.anthropic.com/en/docs/build-with-claude/pdf-support#option-1-url-based-pdf-document
import anthropic
from termcolor import cprint
import json
import time
import os
import base64
import random
import math

from dotenv import load_dotenv
load_dotenv()

# Function to process a question and return Claude's response with retry logic
def process_question(question):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    
    # Load from a local file
    with open("./raw_data/taxInformation.pdf", "rb") as f:
        pdf_data_local = base64.standard_b64encode(f.read()).decode("utf-8")
    
    # Retry parameters
    max_retries = 5
    base_delay = 60  # Start with 60 seconds delay after a rate limit
    
    for attempt in range(1, max_retries + 1):
        try:
            initial_time = time.time()
            cprint(f"Attempt {attempt}/{max_retries} for question: {question[:50]}...", 'cyan')
            
            message = client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=2500,
                system="You are a tax expert. Answer the user's question based on the documents provided, answer in Thai with suitable length",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "url",
                                    "url": "https://www.rd.go.th/fileadmin/user_upload/borkor/tax121260.pdf"
                                }
                            },
                            {
                                "type": "document",
                                "source": {
                                    "type": "url",
                                    "url": "https://www.rd.go.th/fileadmin/user_upload/borkor/taxreturn23072567.pdf"
                                }
                            },
                            {
                                "type": "document",
                                "source": {
                                    "type": "url",
                                    "url": "https://www.rd.go.th/fileadmin/download/tax_deductions_update280168.pdf"
                                }
                            },
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": pdf_data_local
                                }
                            },
                            {
                                "type": "text",
                                "text": question
                            }
                        ]
                    }
                ],
            )
            time_taken = time.time() - initial_time
            
            # Log information about the response
            cprint(f"Successfully processed: {question}", 'cyan')
            cprint(message.content[0].text[:200] + "...", 'magenta')  # Print just first part of the response
            cprint(f"Input token: {message.usage.input_tokens}", 'green')
            cprint(f"Output token: {message.usage.output_tokens}", 'green')
            cprint(f"Cost used: {(message.usage.input_tokens*0.000003)+ (message.usage.output_tokens*0.000015):.2f} dollars", 'red')
            cprint(f"Time taken: {time_taken:.2f} seconds", 'yellow')
            
            return {
                "answer": message.content[0].text,
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
                "cost": (message.usage.input_tokens*0.000003) + (message.usage.output_tokens*0.000015),
                "time_taken": time_taken,
                "attempts": attempt
            }
            
        except anthropic.RateLimitError as e:
            if attempt == max_retries:
                cprint(f"Failed after {max_retries} attempts due to rate limits. Giving up.", 'red')
                raise
            
            # Calculate delay with exponential backoff and jitter
            delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 10)
            cprint(f"Rate limit hit. Waiting for {delay:.1f} seconds before retry {attempt+1}/{max_retries}...", 'yellow')
            time.sleep(delay)
            
        except Exception as e:
            cprint(f"Error: {type(e).__name__}: {str(e)}", 'red')
            if attempt == max_retries:
                cprint(f"Failed after {max_retries} attempts. Giving up.", 'red')
                raise
            
            # For other errors, wait a bit before retrying but with less backoff
            delay = 5 * attempt
            cprint(f"Waiting for {delay} seconds before retry...", 'yellow')
            time.sleep(delay)

# Main function to process all questions
def process_all_questions(test_set_path, output_path):
    # Load the test set
    with open(test_set_path, 'r', encoding='utf-8') as f:
        test_set = json.load(f)
    
    # Check if output file already exists to support resuming
    start_index = 0
    results = None
    
    if os.path.exists(output_path):
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                results = json.load(f)
                
            # Find where we left off
            for i, test_case in enumerate(results["test_cases"]):
                if "inference_result" not in test_case:
                    start_index = i
                    break
            
            if start_index > 0:
                cprint(f"Resuming from question {start_index+1}", 'green')
        except Exception as e:
            cprint(f"Error loading existing results file: {e}", 'red')
            cprint("Starting from the beginning", 'yellow')
    
    # If we couldn't load or resume, start fresh
    if results is None:
        results = test_set.copy()
        # Initialize metrics tracking
        results["overall_metrics"] = {
            "total_cost_usd": 0,
            "total_time_seconds": 0,
            "total_attempts": 0,
            "average_cost_per_question": 0,
            "average_time_per_question": 0,
            "completed_questions": 0
        }
    
    # Process each question
    total_questions = len(results["test_cases"])
    for i in range(start_index, total_questions):
        test_case = results["test_cases"][i]
        cprint(f"Processing question {i+1}/{total_questions}: {test_case['question'][:50]}...", 'blue')
        
        try:
            # Process the question
            result = process_question(test_case["question"])
            
            # Add the inference result to the test case
            test_case["inference_result"] = result["answer"]
            test_case["metrics"] = {
                "input_tokens": result["input_tokens"],
                "output_tokens": result["output_tokens"],
                "cost_usd": result["cost"],
                "time_seconds": result["time_taken"],
                "attempts": result.get("attempts", 1)
            }
            
            # Update total metrics
            results["overall_metrics"]["total_cost_usd"] += result["cost"]
            results["overall_metrics"]["total_time_seconds"] += result["time_taken"]
            results["overall_metrics"]["total_attempts"] += result.get("attempts", 1)
            results["overall_metrics"]["completed_questions"] += 1
            
            # Update averages
            completed = results["overall_metrics"]["completed_questions"]
            results["overall_metrics"]["average_cost_per_question"] = results["overall_metrics"]["total_cost_usd"] / completed
            results["overall_metrics"]["average_time_per_question"] = results["overall_metrics"]["total_time_seconds"] / completed
            
            cprint(f"Successfully processed question {i+1}/{total_questions}", 'green')
        
        except Exception as e:
            cprint(f"Failed to process question {i+1}: {str(e)}", 'red')
            test_case["error"] = str(e)
        
        # Save intermediate results after each question
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Wait between API calls to help avoid rate limiting
        # The delay is dynamic based on the number of input tokens to help stay under the rate limit
        input_tokens = test_case.get("metrics", {}).get("input_tokens", 90000)  # Default high if unknown
        delay = max(60, math.ceil(input_tokens / 1000))  # At least 60 seconds, more for large documents
        cprint(f"Waiting {delay} seconds before the next question to avoid rate limits...", 'yellow')
        time.sleep(delay)
    
    # Save final results
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    return results

if __name__ == "__main__":
    # Define input and output paths
    test_set_path = "tax-test-set.json"
    output_path = "tax-test-results.json"
    
    # Process all questions
    results = process_all_questions(test_set_path, output_path)
    
    # Print summary
    cprint("\nProcessing complete!", 'green')
    cprint(f"Total questions processed: {len(results['test_cases'])}", 'cyan')
    cprint(f"Total cost: ${results['overall_metrics']['total_cost_usd']:.2f}", 'red')
    cprint(f"Total time: {results['overall_metrics']['total_time_seconds']:.2f} seconds", 'yellow')
    cprint(f"Results saved to: {output_path}", 'green')