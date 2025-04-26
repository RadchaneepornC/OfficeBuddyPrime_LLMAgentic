import os
import json
import datetime
import anthropic
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()
import os


class ConversationTracker:
    def __init__(self, model="claude-3-7-sonnet-20250219", max_tokens=1024):
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self.model = model
        self.max_tokens = max_tokens
        self.conversation_history = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0
        
        # Pricing constants for Claude 3.7 Sonnet - per token
        self.pricing = {
            "claude-3-7-sonnet-20250219": {
                "input_per_token": 3.00 / 1000000,  # $3.00 per million input tokens
                "output_per_token": 15.00 / 1000000,  # $15.00 per million output tokens
            }
        }
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on token usage."""
        model_pricing = self.pricing.get(self.model, {"input_per_token": 0, "output_per_token": 0})
        input_cost = input_tokens * model_pricing["input_per_token"]
        output_cost = output_tokens * model_pricing["output_per_token"]
        return input_cost + output_cost
    
    def add_message_to_history(self, role: str, content: List[Dict[str, Any]]) -> None:
        """Add a message to the conversation history."""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def send_message(self, user_message: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send a message to Claude and update conversation history and token counts.
        
        Args:
            user_message: List of content objects for the user message
            
        Returns:
            The complete response from Claude
        """
        # Add user message to history
        self.add_message_to_history("user", user_message)
        
        # Build the messages array from conversation history
        messages = self.conversation_history.copy()
        
        # Send the message to Claude
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=messages
        )
        
        # Extract response content
        assistant_content = response.content
        
        # Add assistant response to history
        self.add_message_to_history("assistant", assistant_content)
        
        # Update token counts and cost
        self.total_input_tokens += response.usage.input_tokens
        self.total_output_tokens += response.usage.output_tokens
        
        message_cost = self.calculate_cost(
            response.usage.input_tokens, 
            response.usage.output_tokens
        )
        self.total_cost += message_cost
        
        # Add usage metrics to the response object for easier access
        response_with_metrics = {
            "response": response,
            "message_text": response.content[0].text if response.content else "",
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "message_cost": message_cost,
                "total_input_tokens": self.total_input_tokens,
                "total_output_tokens": self.total_output_tokens,
                "total_cost": self.total_cost
            }
        }
        
        return response_with_metrics
    
    def get_raw_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the raw conversation history."""
        return self.conversation_history
    
    def get_plain_text_history(self) -> str:
        """Get the conversation history in a readable plain text format."""
        history_text = ""
        for message in self.conversation_history:
            role = message["role"]
            
            if role == "user":
                text_content = self._extract_text_from_content(message["content"])
                history_text += f"User: {text_content}\n\n"
            else:  # assistant
                if isinstance(message["content"], list):
                    for content_item in message["content"]:
                        if content_item.get("type") == "text":
                            history_text += f"Assistant: {content_item.get('text', '')}\n\n"
                else:
                    history_text += f"Assistant: {message['content']}\n\n"
                    
        return history_text
    
    def _extract_text_from_content(self, content: List[Dict[str, Any]]) -> str:
        """Extract text from content list."""
        text_parts = []
        for item in content:
            if item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        return " ".join(text_parts)
    
    def save_to_json(self, filepath: str) -> None:
        """
        Save the conversation history, token usage, and cost data to a JSON file.
        
        Args:
            filepath: Path to the output JSON file
        """
        # Create a simplified serializable version of the conversation history
        serializable_history = []
        for message in self.conversation_history:
            serialized_message = {
                "role": message["role"]
            }
            
            # Handle content based on its type
            if message["role"] == "user":
                # For user messages, extract text content
                text_parts = []
                docs = []
                
                for item in message["content"]:
                    if item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                    elif item.get("type") == "document":
                        docs.append(item.get("source", {}).get("url", ""))
                
                serialized_message["text"] = " ".join(text_parts)
                if docs:
                    serialized_message["documents"] = docs
            else:
                # For assistant messages, convert complex object to plain text
                if isinstance(message["content"], list):
                    serialized_message["text"] = ""
                    for content_item in message["content"]:
                        if hasattr(content_item, "text"):
                            serialized_message["text"] += content_item.text
                        elif isinstance(content_item, dict) and "text" in content_item:
                            serialized_message["text"] += content_item["text"]
                        elif isinstance(content_item, str):
                            serialized_message["text"] += content_item
                else:
                    # Try to extract text in various possible formats
                    if hasattr(message["content"], "text"):
                        serialized_message["text"] = message["content"].text
                    elif isinstance(message["content"], str):
                        serialized_message["text"] = message["content"]
                    else:
                        serialized_message["text"] = str(message["content"])
            
            serializable_history.append(serialized_message)
            
        # Create the data structure to save
        data = {
            "conversation_history": serializable_history,
            "usage_statistics": {
                "model": self.model,
                "total_messages": len(self.conversation_history) // 2,  # User-assistant pairs
                "total_input_tokens": self.total_input_tokens,
                "total_output_tokens": self.total_output_tokens,
                "total_tokens": self.total_input_tokens + self.total_output_tokens,
                "total_cost": self.total_cost
            },
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get a summary of token usage and cost."""
        return {
            "model": self.model,
            "total_messages": len(self.conversation_history) // 2,  # User-assistant pairs
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost": self.total_cost
        }


# Example usage with multi-turn loop and JSON saving
if __name__ == "__main__":
    # Initialize the conversation tracker
    conversation = ConversationTracker(model="claude-3-7-sonnet-20250219", max_tokens=1024)
    
    # Get user's initial message
    text_user = input("พิมพ์ข้อความของคุณเพื่อจะเริ่มต้นบทสนทนา... : ")
    
    # First message with documents
    initial_message = [
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
            "type": "text",
            "text": text_user
        }
    ]
    
    # Send the first message
    print("\nSending your message to Claude...")
    response = conversation.send_message(initial_message)
    
    # Print the first response
    print("\nClaude's response:")
    print(response["message_text"])
    print("\nUsage for this message:")
    print(f"Input tokens: {response['usage']['input_tokens']}")
    print(f"Output tokens: {response['usage']['output_tokens']}")
    print(f"Message cost: ${response['usage']['message_cost']:.6f}")
    
    # Start the multi-turn loop
    print("\n" + "-"*50)
    print("Multi-turn conversation started. Type 'quit' to exit.")
    print("-"*50 + "\n")
    
    while True:
        # Get user input
        user_input = input("\nYour message (type 'quit' to exit): ")
        
        # Check if user wants to quit
        if user_input.lower() == 'quit':
            print("\nExiting conversation...")
            break
        
        # Create user message
        user_message = [
            {
                "type": "text",
                "text": user_input
            }
        ]
        
        # Send message and get response
        response = conversation.send_message(user_message)
        
        # Print the response
        print("\nClaude's response:")
        print(response["message_text"])
        
        # Print usage for this message
        print("\nUsage for this message:")
        print(f"Input tokens: {response['usage']['input_tokens']}")
        print(f"Output tokens: {response['usage']['output_tokens']}")
        print(f"Message cost: ${response['usage']['message_cost']:.6f}")
    
    # Print overall conversation summary
    print("\nOverall conversation summary:")
    usage_summary = conversation.get_usage_summary()
    print(f"Total messages: {usage_summary['total_messages']}")
    print(f"Total input tokens: {usage_summary['total_input_tokens']}")
    print(f"Total output tokens: {usage_summary['total_output_tokens']}")
    print(f"Total tokens: {usage_summary['total_tokens']}")
    print(f"Total cost: ${usage_summary['total_cost']:.6f}")
    
    # Save conversation history and stats to JSON
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_filename = f"conversation_history_{timestamp}.json"
    saved_path = conversation.save_to_json(json_filename)
    
    print(f"\nConversation history and stats saved to: {saved_path}")
    
    # Print the plain text conversation history as well
    print("\nConversation history:")
    print(conversation.get_plain_text_history())