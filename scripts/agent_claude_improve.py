# https://docs.anthropic.com/en/docs/build-with-claude/pdf-support#option-1-url-based-pdf-document
import anthropic
from termcolor import cprint

from dotenv import load_dotenv
load_dotenv()
import os
import base64
import httpx
import time

user_input = input("พิมพิ์คำถามเกี่ยวกับภาษีของคุณได้ที่นี่: ")

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

#Load from a local file
with open("./data/taxInformation.pdf", "rb") as f:
    pdf_data_local = base64.standard_b64encode(f.read()).decode("utf-8")

initial_time = time.time()
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
time_taken = time.time() - initial_time

# cprint(message)
cprint(message.content[0].text, 'magenta')
cprint(f"Input token: {message.usage.input_tokens}", 'green')
cprint(f"Output token: {message.usage.output_tokens}", 'green')
cprint(f"Cost used: {(message.usage.input_tokens*0.000003)+ (message.usage.output_tokens*0.000015):.2f} dollars", 'red')
cprint(f"Time taken: {time_taken:.2f} seconds", 'yellow')

# Q1: "ถ้ามีรายได้ต่อปี ไม่ถึง 500,000 บาท ต้องยื่นภาษีหรือไม่?"
# Answer as below:
#[TextBlock(citations=None, text='ตามข้อมูลในเอกสารที่คุณแนบมา ถ้ามีรายได้ต่อปีไม่ถึง 500,000 บาท ต้องพิจารณาดังนี้:\n\n- ถ้ามีเงินได้สุทธิไม่เกิน 150,000 บาท ได้รับการยกเว้นภาษี (ไม่ต้องเสียภาษี)\n- ถ้ามีเงินได้สุทธิอยู่ระหว่าง 150,001-300,000 บาท จะเสียภาษีในอัตรา 5% เฉพาะส่วนที่เกิน 150,000 บาท\n- ถ้ามีเงินได้สุทธิอยู่ระหว่าง 300,001-500,000 บาท จะเสียภาษีในอัตรา 10% เฉพาะส่วนที่เกิน 300,000 บาท\n\nอย่างไรก็ตาม การยื่นภาษีและการเสียภาษีเป็นคนละเรื่องกัน โดยทั่วไปผู้มีเงินได้มีหน้าที่ต้องยื่นแบบแสดงรายการภาษี แม้ว่าจะไม่ต้องเสียภาษีก็ตาม (เช่น กรณีมีเงินได้สุทธิไม่เกิน 150,000 บาท) ทั้งนี้เพื่อเป็นการแจ้งรายได้ต่อกรมสรรพากร', type='text')]

# Q2: "ค่าเบี้ยงเลี้ยงต้องนำมาคิดรวมภาษีหรือไม่?"
# Answer as below:
# Message(id='msg_01WjQKzdAtUu9Rsxk1Yw7DoN', content=[TextBlock(citations=None, text='# สรุปข้อมูลเกี่ยวกับภาษีเงินได้บุคคลธรรมดา\n\n## เกี่ยวกับค่าเบี้ยเลี้ยงและภาษี\n\nจากเอกสารที่ให้มา ค่าเบี้ยเลี้ยงที่ลูกจ้างได้รับจากนายจ้าง ไม่ต้องนำมารวมคำนวณเพื่อเสียภาษีเงินได้ในกรณีต่อไปนี้:\n\n1. ค่าเบี้ยเลี้ยงที่ลูกจ้างหรือผู้ปฏิบัติงานจ่ายไปโดยสุจริตตามความจำเป็น เฉพาะในการปฏิบัติหน้าที่ของตน และได้จ่ายไปทั้งหมดในการนั้น (ตามข้อ 1 ในเอกสารที่ 2)\n\n2. ค่าพาหนะและเบี้ยเลี้ยงเดินทางตามอัตราที่รัฐบาลกำหนดโดยพระราชกฤษฎีกา (ตามข้อ 2 ในเอกสารที่ 2)\n\n3. เงินค่าเดินทางที่นายจ้างจ่ายให้ลูกจ้างเฉพาะส่วนที่ลูกจ้างได้จ่ายทั้งหมดโดยจำเป็นเพื่อการเดินทางจากต่างถิ่นในการเข้ารับงานหรือเมื่อการจ้างสิ้นสุดลง (ตามข้อ 3 ในเอกสารที่ 2)\n\n## อัตราภาษีเงินได้บุคคลธรรมดา (เริ่มใช้ปีภาษี 2560)\n\n| เงินได้สุทธิ (บาท) | อัตราภาษี (ร้อยละ) |\n|-----------------|-----------------|\n| 1 - 150,000 | ได้รับยกเว้น |\n| 150,001 - 300,000 | 5 |\n| 300,001 - 500,000 | 10 |\n| 500,001 - 750,000 | 15 |\n| 750,001 - 1,000,000 | 20 |\n| 1,000,001 - 2,000,000 | 25 |\n| 2,000,001 - 5,000,000 | 30 |\n| 5,000,001 บาทขึ้นไป | 35 |\n\nหมายเหตุ: เงินได้สุทธิส่วนที่ไม่เกิน 150,000 บาท ยังคงได้รับยกเว้นตามพระราชกฤษฎีกา\n\n## สรุป\n\nค่าเบี้ยเลี้ยงที่ลูกจ้างได้รับจากนายจ้าง ไม่ต้องนำมารวมคำนวณเพื่อเสียภาษีเงินได้ หากเป็นไปตามเงื่อนไขที่กฎหมายกำหนด โดยเฉพาะกรณี', type='text')], model='claude-3-7-sonnet-20250219', role='assistant', stop_reason='max_tokens', stop_sequence=None, type='message', usage=Usage(cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=91435, output_tokens=1024))

# Q3: เงินบริจาคให้นักการเมืองสามารถนำมาลดหย่อนภาษีได้หรือไม่?
# Answer as below:
# Message(id='msg_011TnehJnhR5RPfVXRHpm37u', content=[TextBlock(citations=None, text='จากเอกสารที่ให้มา ผมสามารถตอบคำถามเกี่ยวกับการบริจาคให้นักการเมืองกับการลดหย่อนภาษีได้ดังนี้\n\nใช่ครับ เงินบริจาคให้พรรคการเมืองสามารถนำมาลดหย่อนภาษีได้ ตามข้อมูลในเอกสาร "ผู้มีเงินได้มีสิทธิหักลดหย่อนอะไรได้บ้าง?" ระบุไว้ในข้อที่ 27 ว่า:\n\n"เงินบริจาคให้แก่พรรคการเมือง เงิน ทรัพย์สิน หรือประโยชน์อื่นใดที่ให้เพื่อสนับสนุนการจัดกิจกรรมระดมทุนของพรรคการเมือง หักลดหย่อนเท่าที่จ่ายจริง แต่ไม่เกิน 10,000 บาท"\n\nสรุปคือ คุณสามารถนำเงินที่บริจาคให้พรรคการเมืองมาหักลดหย่อนภาษีได้ตามจำนวนที่จ่ายจริง แต่สูงสุดไม่เกิน 10,000 บาทต่อปีภาษี', type='text')], model='claude-3-7-sonnet-20250219', role='assistant', stop_reason='end_turn', stop_sequence=None, type='message', usage=Usage(cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=91438, output_tokens=452))
# จากเอกสารที่ให้มา ผมสามารถตอบคำถามเกี่ยวกับการบริจาคให้นักการเมืองกับการลดหย่อนภาษีได้ดังนี้


# ใช่ครับ เงินบริจาคให้พรรคการเมืองสามารถนำมาลดหย่อนภาษีได้ ตามข้อมูลในเอกสาร "ผู้มีเงินได้มีสิทธิหักลดหย่อนอะไรได้บ้าง?" ระบุไว้ในข้อที่ 27 ว่า:

# "เงินบริจาคให้แก่พรรคการเมือง เงิน ทรัพย์สิน หรือประโยชน์อื่นใดที่ให้เพื่อสนับสนุนการจัดกิจกรรมระดมทุนของพรรคการเมือง หักลดหย่อนเท่าที่จ่ายจริง แต่ไม่เกิน 10,000 บาท"

# สรุปคือ คุณสามารถนำเงินที่บริจาคให้พรรคการเมืองมาหักลดหย่อนภาษีได้ตามจำนวนที่จ่ายจริง แต่สูงสุดไม่เกิน 10,000 บาทต่อปีภาษี
