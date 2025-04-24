# https://github.com/daveebbelaar/ai-cookbook/blob/main/patterns/workflows/1-introduction/4-retrieval.py

import json
import os

from openai import OpenAI
from pydantic import BaseModel, Field

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

"""
docs: https://platform.openai.com/docs/guides/function-calling
"""

import os
print(f"Current working directory: {os.getcwd()}")



# --------------------------------------------------------------
# Define the knowledge base retrieval tool
# --------------------------------------------------------------


# def search_kb(question: str):
#     """
#     Load the whole knowledge base from the JSON file.
#     (This is a mock function for demonstration purposes, we don't search)
#     """
#     with open("knowledgeBase.json", "r") as f:
#         return json.load(f)

def search_kb(question: str):
    """
    Load the whole knowledge base from the JSON file.
    (This is a mock function for demonstration purposes, we don't search)
    """
    file_path = os.path.join(os.path.dirname(__file__), "knowledgeBase.json")
    try:
        with open(file_path, "r", encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return {"error": "Knowledge base file not found"}
    except json.JSONDecodeError:
        print("Error: Invalid JSON in knowledgeBase.json")
        return {"error": "Invalid knowledge base format"}


# --------------------------------------------------------------
# Step 1: Call model with search_kb tool defined
# --------------------------------------------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_kb",
            "description": "Get the answer to the user's question from the knowledge base.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                },
                "required": ["question"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]

system_prompt = "You are a helpful assistant that answers questions from the knowledge base about Thai TAX."

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "ขอลดหย่อนภาษีอย่างไหรได้บ้าง"},
]

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
)
print(completion)
print(completion.choices[0].message.content)

# --------------------------------------------------------------
# Step 2: Model decides to call function(s)
# --------------------------------------------------------------

completion.model_dump()

# --------------------------------------------------------------
# Step 3: Execute search_kb function
# --------------------------------------------------------------


def call_function(name, args):
    if name == "search_kb":
        return search_kb(**args)


for tool_call in completion.choices[0].message.tool_calls:
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    messages.append(completion.choices[0].message)

    result = call_function(name, args)
    messages.append(
        {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)}
    )

# --------------------------------------------------------------
# Step 4: Supply result and call model again
# --------------------------------------------------------------


class KBResponse(BaseModel):
    answer: str = Field(description="The answer to the user's question.")
    source: int = Field(description="The record id of the answer.")


completion_2 = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    response_format=KBResponse,
)

# --------------------------------------------------------------
# Step 5: Check model response
# --------------------------------------------------------------

final_response = completion_2.choices[0].message.parsed
print(final_response.answer)
print(final_response.source)
print(final_response)

# # --------------------------------------------------------------
# # Question that doesn't trigger the tool
# # --------------------------------------------------------------

# messages = [
#     {"role": "system", "content": system_prompt},
#     {"role": "user", "content": "What is the weather in Tokyo?"},
# ]

# completion_3 = client.beta.chat.completions.parse(
#     model="gpt-4o",
#     messages=messages,
#     tools=tools,
# )

# completion_3.choices[0].message.content
