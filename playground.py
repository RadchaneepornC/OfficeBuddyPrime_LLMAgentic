# Try using LLM API from OpenRouter API 
import os
import backoff
# from curl_cffi import CurlError
from requests.exceptions import RequestException
import logging
from openai import OpenAI
import openai
import os
import json
import requests
import argparse
import re
from termcolor import cprint
from typing import Dict, List, Tuple, Optional, Callable, Any
from prompt import router_agent as router_agent

from dotenv import load_dotenv
load_dotenv()

class RouterAgent:
    
    """classification agent whether the question is about tax or labor law"""

    def __init__(self):
        """
        Initialize the MonitoringAgent.

        Args:
            stage (str): Current conversation stage
            approach (str): Conversation approach
            model (str): Model identifier for API calls
        """
      
        self.client = OpenAI(base_url="https://openrouter.ai/api/v1",
                            api_key=os.environ["OPENROUTER_API_KEY"])


    @backoff.on_exception(
        backoff.expo, 
        (openai.RateLimitError, openai.APIError),
        max_tries=3,
        logger=logging.getLogger(__name__)
    )
    
    def request_call(self, user_input) -> str:
    
        try:
            system_prompt = router_agent
            prompt_user_input = f"This is user input message for classification: {user_input}"
            
            response = self.client.chat.completions.create(
                model="deepseek/deepseek-chat-v3-0324:free", 
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt 
                    },
                    {
                        "role": "user",
                        "content": prompt_user_input
                    }
                ],
                temperature=0.7,
            )
            
            # Access the response correctly for chat completions
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"Error in API call: {str(e)}")
            raise

    def extract_xml(self, text: str, tag: str) -> str:
        """
        Extracts the content of the specified XML tag from the given text.

        Args:
            text (str): The text containing the XML.
            tag (str): The XML tag to extract content from.

        Returns:
            str: The content of the specified XML tag, or an empty string if the tag is not found.
        """
        match = re.search(f'<{tag}>(.*?)</{tag}>', text, re.DOTALL)
        return match.group(1).strip() if match else ""

   
    def agent_decision(self, user_input: str = "") -> Tuple[str, str]:
        """
        Makes a decision based on the conversation history.

        Args:
            history_conversation (List[Dict[str, str]]): The conversation history.

        Returns:
            Tuple[str, str]: The decision and feedback extracted from the response.
        """
        
        
        response = self.request_call(user_input=input('สวัสดี iLabor ยินดีต้อนรับ กรุณาใส่คำถามของคุณ: '))

        decision = self.extract_xml(response, 'decision')
        feedback = self.extract_xml(response, 'reason')

        return decision, feedback

def main():
    agent = RouterAgent()
    decision, feedback = agent.agent_decision()
    print(f"Decision: {decision}")
    print(f"Reason: {feedback}")

if __name__ == "__main__":
    main()




# =============== testing API =========================
# client = OpenAI(
#   base_url="https://openrouter.ai/api/v1",
#   api_key=os.environ["OPENROUTER_API_KEY"],
# )

# completion = client.chat.completions.create(
# #   extra_headers={
# #     "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
# #     "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
# #   },
#   extra_body={},
#   model="deepseek/deepseek-chat-v3-0324:free",
#   messages=[
#     {
#       "role": "user",
#       "content": "สวัสดี"
#     }
#   ]
# )

# cprint(completion, "red")
# print()
# cprint(completion.choices[0].message.content, "green")
# ChatCompletion(id='gen-1745134197-16gKYLyygK5uS0GgLKWB', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='สวัสดีค่ะ! 😊 มีอะไรให้ช่วยไหมคะ?', refusal=None, role='assistant', annotations=None, audio=None, function_call=None, tool_calls=None, reasoning=None), native_finish_reason='stop')], created=1745134197, model='deepseek/deepseek-chat-v3-0324', object='chat.completion', service_tier=None, system_fingerprint=None, usage=CompletionUsage(completion_tokens=17, prompt_tokens=7, total_tokens=24, completion_tokens_details=None, prompt_tokens_details=None), provider='Targon')



# =============== testing API =========================