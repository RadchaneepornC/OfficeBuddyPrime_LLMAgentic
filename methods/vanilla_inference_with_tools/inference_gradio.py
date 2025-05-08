import gradio as gr
import anthropic
import os
import base64
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# Function to process user query
def process_query(user_input):
    start_time = time.time()
    
    # Load PDF data
    with open("./raw_data/taxInformation.pdf", "rb") as f:
        pdf_data_local = base64.standard_b64encode(f.read()).decode("utf-8")
    
    # Make API call to Claude
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
                        "text": user_input
                    }
                ]
            }
        ],
    )
    
    # Calculate metrics
    time_taken = time.time() - start_time
    input_tokens = message.usage.input_tokens
    output_tokens = message.usage.output_tokens
    cost = (input_tokens * 0.000003) + (output_tokens * 0.000015)
    
    # Extract response text
    response_text = message.content[0].text
    
    # Create metrics summary
    metrics = f"""
    Input tokens: {input_tokens}
    Output tokens: {output_tokens}
    Cost: ${cost:.4f}
    Time taken: {time_taken:.2f} seconds
    """
    
    return response_text, metrics

# Create Gradio interface
with gr.Blocks(theme=gr.themes.Soft(), title="Thai Tax Advisor (TH)") as demo:
    gr.Markdown("# iLabour: TAX Buddy for Thai people")
    gr.Markdown("#### แชทบอท ถาม-ตอบ ภาษีเงินได้บุคคลธรรมดา")
    
    with gr.Row():
        with gr.Column(scale=2):
            input_text = gr.Textbox(
                label="พิมพ์คำถามเกี่ยวกับภาษีของคุณได้ที่นี่",
                placeholder="ตัวอย่าง: ถ้ามีรายได้ต่อปี ไม่ถึง 500,000 บาท ต้องยื่นภาษีหรือไม่?",
                lines=3
            )
            submit_btn = gr.Button("ส่งคำถาม", variant="primary")
        
        with gr.Column(scale=3):
            output_text = gr.Markdown(label="คำตอบ")
    
    with gr.Row():
        metrics_output = gr.Textbox(label="สถิติการใช้งาน", lines=4, interactive=False)
    
    # Examples
    gr.Examples(
        [    
            ["อยากทราบวิธีการยื่นแบบภาษีเงินได้บุคคลธรรมดา"],
            ["ถ้ามีรายได้ต่อปี ไม่ถึง 500,000 บาท ต้องยื่นภาษีหรือไม่?"],
            ["ค่าเบี้ยงเลี้ยงต้องนำมาคิดรวมภาษีหรือไม่?"],
            ["ประเภทเงินได้ที่ได้รับยกเว้นภาษีมีอะไรบ้าง?"],
            ["เงินบริจาคให้นักการเมืองสามารถนำมาลดหย่อนภาษีได้หรือไม่?"],
            ["ยื่นแบบแสดงภาษีได้ที่ไหนบ้าง?"],
            ["วิธีการคํานวณภาษีเงินได้บุคคลธรรมดาสิ้นปี"],
        ],
        input_text
    )
    
    # Set up event handler
    submit_btn.click(
        fn=process_query,
        inputs=input_text,
        outputs=[output_text, metrics_output]
    )
    
    input_text.submit(
        fn=process_query,
        inputs=input_text,
        outputs=[output_text, metrics_output]
    )

if __name__ == "__main__":
    demo.launch(debug=True, share=True)