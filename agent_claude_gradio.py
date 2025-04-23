import gradio as gr
import anthropic
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def query_claude(question, url1, url2, url3):
    # Prepare content list with documents
    content = []
    
    # Add URLs if provided
    if url1.strip():
        content.append({
            "type": "document",
            "source": {
                "type": "url",
                "url": url1.strip()
            }
        })
    
    if url2.strip():
        content.append({
            "type": "document",
            "source": {
                "type": "url",
                "url": url2.strip()
            }
        })
    
    if url3.strip():
        content.append({
            "type": "document",
            "source": {
                "type": "url",
                "url": url3.strip()
            }
        })
    
    # Add the question
    content.append({
        "type": "text",
        "text": question
    })
    
    # Create message request
    try:
        message = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ],
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="Claude Document Q&A", theme='allenai/gradio-theme') as demo:
    gr.Markdown("# iLabour: TAX Buddy for Thai people")
    gr.Markdown("Ask questions about your tax")
    
    with gr.Row():
        with gr.Column():
            # Input components
            url1 = gr.Textbox(
                label="Document URL 1", 
                placeholder="https://example.com/document1.pdf",
                value="https://www.rd.go.th/fileadmin/user_upload/borkor/tax121260.pdf"
            )
            url2 = gr.Textbox(
                label="Document URL 2 (Optional)", 
                placeholder="https://example.com/document2.pdf",
                value="https://www.rd.go.th/fileadmin/user_upload/borkor/taxreturn23072567.pdf"
            )
            url3 = gr.Textbox(
                label="Document URL 3 (Optional)", 
                placeholder="https://example.com/document3.pdf",
                value="https://www.rd.go.th/fileadmin/download/tax_deductions_update280168.pdf"
            )
            question = gr.Textbox(
                label="Your Question", 
                placeholder="Enter your question here..."
            )
            submit_btn = gr.Button("Submit")
        
        with gr.Column():
            # Output component
            answer = gr.Markdown(label="Claude's Response")
    
    # Connect the function
    submit_btn.click(
        fn=query_claude,
        inputs=[question, url1, url2, url3],
        outputs=answer
    )

# Launch the app
if __name__ == "__main__":
    demo.launch(share=True)