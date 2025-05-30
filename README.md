
#  iLabour: LLM based TAX Buddy chatbot for Thai people

#### แชทบอท ถาม-ตอบ ภาษีเงินได้บุคคลธรรมดา

## Group Project of Chula NLP Class 2025
Our group qualified for ✨ the final championround (top 8 of 32 groups)✨ in the Chula NLP class project.

## Members:
- Thatphum Paonim
- Ayuth Mangmesap
- Radchaneeporn Changpun

## Objective: 
To conduct an empirical study comparing both techniques  `I) RAG` and `II) Vanilla inference with tools used (agentic-like)` to answer about **Thai Personal Income Tax : PIT**

## Technical Methods we used:
-  Preprocess Data
    - OCR
    - web scraping
- LLM based Techniques
    - RAG (Naive RAG & Agentic RAG)
    - Vanilla Inference with tool used (Inference with long context)
- Evaluation
    - LLM as a judged
    - Automatic Evaluation Metric : BERT Score, BLUE, ROUGE-l
    - Qualitative Analysis by human


## Results

| Method | Upstream Evaluation | Average BERT Score-F1 |  ROUGE-L F1 | BLEU-4 | 4.1o-mini as a Judge (1-5) |
|--------|---------------------|----------------------------------|--------------------------------|-------------------------------|---------------------------------------------------|
| 1. Agentic RAG Claude 3.7 Sonnet | MRR 0.91 | 0.9186| 0.5655| 0.3941| 4.8| 
| 2. Naive RAG R1-32B-Qwen Model| MRR 0.91 |0.9120| 0.5334 | 0.3603| 4.3 |
| 3. Long Context Claude 3.7 Sonnet | - |0.8870 |0.4219 |0.2725 | 4.5| 
| 4. Claude 3.7 Sonnet  | - | 0.8797 |0.3664 |0.2184 | 3.7 | 

## Presentation slide
[Slide Link](https://docs.google.com/presentation/d/1f0aijNcMq-LiEN8I8WaDgFDmKHLDNuGvK4xCbjN8bRA/edit?usp=sharing)


## Result Analysis


## Conclusion and Recommend for further studies
