import json
import os

from openai import OpenAI
from pydantic import BaseModel, Field

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print(f"Current working directory: {os.getcwd()}")

# --------------------------------------------------------------
# Define the knowledge base retrieval tool
# --------------------------------------------------------------

def search_kb(question: str):
    """
    Search the knowledge base for relevant information based on the question
    """
    file_path = os.path.join(os.path.dirname(__file__), "knowledgeBase.json")
    try:
        with open(file_path, "r", encoding='utf-8') as f:
            kb_data = json.load(f)
            
        # The key difference - your JSON has a "records" array
        if "records" in kb_data:
            kb = kb_data["records"]
        else:
            # Fallback in case the structure is different
            kb = kb_data
        
        # Simple keyword-based search
        keywords = question.lower().split()
        # Add Thai tax-related keywords
        tax_keywords = ["ภาษี", "ลดหย่อน", "เงินได้", "ยกเว้น", "ชำระ", "ยื่นแบบ"]
        keywords.extend(tax_keywords)
        
        relevant_entries = []
        # Score each entry based on keyword matches
        for entry in kb:
            if isinstance(entry, dict) and "question" in entry and "answer" in entry:
                score = 0
                for keyword in keywords:
                    if keyword in entry["question"].lower():
                        score += 2  # Higher weight for matches in the question
                    if keyword in entry["answer"].lower():
                        score += 1
                
                if score > 0:
                    relevant_entries.append({"entry": entry, "score": score})
        
        # Sort by relevance score and take top 3
        relevant_entries.sort(key=lambda x: x["score"], reverse=True)
        results = [item["entry"] for item in relevant_entries[:3]]
        
        if not results:
            # If no matches, return a generic entry
            if len(kb) > 0:
                return [kb[0]]
            return {"error": "No relevant information found"}
            
        return results
        
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return {"error": "Knowledge base file not found"}
    except json.JSONDecodeError:
        print("Error: Invalid JSON in knowledgeBase.json")
        return {"error": "Invalid knowledge base format"}
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}

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

user_input = input("พิมพิ์คำถามเกี่ยวกับภาษีที่คุณสงสัย: ")
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_input},
]

# --------------------------------------------------------------
# Step 2: Call the model for initial completion
# --------------------------------------------------------------

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
)
print("Initial completion decision:")
print(completion.choices[0].message.content or "No content - using tool")

# --------------------------------------------------------------
# Step 3: Execute search_kb function if model calls it
# --------------------------------------------------------------

def call_function(name, args):
    if name == "search_kb":
        return search_kb(**args)

# Check if tool calls exist
if hasattr(completion.choices[0].message, 'tool_calls') and completion.choices[0].message.tool_calls:
    for tool_call in completion.choices[0].message.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        messages.append(completion.choices[0].message)

        result = call_function(name, args)
        # Convert result to JSON string
        result_str = json.dumps(result, ensure_ascii=False)
        
        print(f"\nKnowledge base search results (truncated):")
        print(f"{result_str[:500]}... (truncated)")
        
        messages.append(
            {"role": "tool", "tool_call_id": tool_call.id, "content": result_str}
        )

    # --------------------------------------------------------------
    # Step 4: Call model again with search results - FIXED JSON FORMAT REQUIREMENT
    # --------------------------------------------------------------
    
    # Add instruction to return JSON format explicitly
    messages.append({
        "role": "user", 
        "content": "Based on the search results, please provide information about tax deductions in Thailand. Format your response as a JSON object with 'answer' and 'source' fields."
    })
    
    completion_2 = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={"type": "json_object"},
    )

    # Extract the response
    response_content = completion_2.choices[0].message.content
    print("\nFinal response from model:")
    print(response_content)
    
    try:
        parsed_response = json.loads(response_content)
        print("\nParsed response:")
        print(f"Answer: {parsed_response.get('answer', 'No answer found')}")
        print(f"Source: {parsed_response.get('source', 'No source found')}")
    except json.JSONDecodeError:
        print("Error parsing JSON response")

else:
    print("Model responded directly without using tools")