
#  iLabour: LLM based TAX Buddy chatbot for Thai people

#### แชทบอท ถาม-ตอบ ภาษีเงินได้บุคคลธรรมดา

## Group Project of Chula NLP Class 2025

## Members:
- Thatphum Paonim
- Ayuth Mangmesap
- Radchaneeporn Changpun

## Objective: 
To conduct an empirical study comparing both techniques  `I) RAG` and `II) Vanilla inference with tools used (agentic-like)` to answer about **Thai Personal Income Tax : PIT**

## Technical Methods we used:
- [1] Preprocess Data
    - OCR
    - web scraping
- [1] LLM based Techniques
    - RAG
    - Vanilla Inference with tool used (Agentic liked)
- [1] Evaluation
    - LLM as a judged
    - Automatic Evaluation Metric : BERT Score, BLUE, ROUGE-l
    - Qualitative Analysis by human


## Results

| Method | Upstream Evaluation | Qualitative Result | Average BERT Score-F1 |  ROUGE-L F1 | BLEU-4 | LLM as a Judge (Win Rate %) | Downstream Evaluation - LLM as a Judge (Win rate) |
|--------|---------------------|------------------------------------------|----------------------------------|--------------------------------|-------------------------------|---------------------------------------------------|--------------------------------------------------|
| 1. RAG 1-Proprietary Model | Score XX.XX |:heavy_check_mark: | | | | | |
| 2. RAG 2-Opensource Model| Score XX.XX |:heavy_multiplication_x:| | | | | |
| 3. Vanilla Inference with Anthropic Tools | - | 0.8870 |0.4219 |0.2725 | | | |


## Result Analysis


## Conclusion and Recommend for further studies