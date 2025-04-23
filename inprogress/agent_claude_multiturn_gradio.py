import os
import json
import datetime
import anthropic
import gradio as gr
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()


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


def create_simple_chatbot_interface():
    # Initialize conversation tracker
    conversation = ConversationTracker(model="claude-3-7-sonnet-20250219", max_tokens=1024)
    
    # Store document URLs
    pdf_urls = []
    
    def add_pdf_url(url_input):
        """Add a PDF URL to the context"""
        if url_input.strip():
            pdf_urls.append(url_input.strip())
            return f"Added PDF URL: {url_input.strip()}", ""
        return "", ""
    
    def clear_urls():
        """Clear all PDF URLs"""
        pdf_urls.clear()
        return "All PDF URLs cleared"
    
    def send_message(user_input):
        """Send message to Claude with PDF URLs in context"""
        if not user_input.strip():
            return ""
        
        # Create message content with PDFs and user input
        message_content = []
        
        # Add document URLs first
        for url in pdf_urls:
            message_content.append({
                "type": "document",
                "source": {
                    "type": "url",
                    "url": url
                }
            })
        
        # Add user text
        message_content.append({
            "type": "text",
            "text": user_input
        })
        
        # Send message to Claude
        response = conversation.send_message(message_content)
        
        # Return Claude's response text
        return response["message_text"]
    
    # Create Gradio interface
    with gr.Blocks(title="Simple Claude Chatbot",theme='allenai/gradio-theme') as interface:
        gr.Markdown("# Simple Claude 3.7 Chatbot")
        
        with gr.Row():
            with gr.Column():
                url_input = gr.Textbox(
                    label="Enter PDF URL",
                    placeholder="https://example.com/document.pdf"
                )
                add_btn = gr.Button("Add PDF URL")
                clear_btn = gr.Button("Clear All URLs")
                url_status = gr.Textbox(label="URL Status", interactive=False)
        
        with gr.Row():
            with gr.Column():
                user_input = gr.Textbox(
                    label="Your Message",
                    placeholder="Type your message here...",
                    lines=3
                )
                send_btn = gr.Button("Send Message")
                response_output = gr.Textbox(
                    label="Claude's Response",
                    interactive=False,
                    lines=10
                )
        
        # Connect components
        add_btn.click(
            fn=add_pdf_url,
            inputs=[url_input],
            outputs=[url_status, url_input]
        )
        
        clear_btn.click(
            fn=clear_urls,
            inputs=[],
            outputs=[url_status]
        )
        
        send_btn.click(
            fn=send_message,
            inputs=[user_input],
            outputs=[response_output]
        )
        
        user_input.submit(
            fn=send_message,
            inputs=[user_input],
            outputs=[response_output]
        )
        
    return interface

# Run the app if executed directly
if __name__ == "__main__":
    interface = create_simple_chatbot_interface()
    interface.launch(share=True)