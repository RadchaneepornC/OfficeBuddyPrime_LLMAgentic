
#  iLabour: LLM based TAX Buddy chatbot for Thai people

#### แชทบอท ถาม-ตอบ ภาษีเงินได้บุคคลธรรมดา

## Group Project of Chula NLP Class 2025
Our group qualified for ✨ the final champion round (top 8 of 32 groups)✨ in the Chula NLP class project.

## Members:
- Thatphum Paonim
- Ayuth Mangmesap
- Radchaneeporn Changpun

## Objective: 
To conduct an empirical study comparing LLM techniques to answer about **Thai Personal Income Tax : PIT**. 
The techniques we adopt to use in this study are following:
- Agentic RAG with proprietary LLM (Claude 3.7 sonnet)
- Naive RAG with opensource LLM (Qwen 32B)
- Long Context proprietary LLM inferencing (Claude 3.7 sonnet)
- Vanilla proprietary LLM interencing (Claude 3.7 sonnet)

## Technical Methods we used:
-  Preprocess Data
    - OCR
    - Web scraping
- LLM based Techniques
    - RAG (Naive RAG & Agentic RAG)
    - Vanilla Inference with tool used (Inference with long context)
- Evaluation
    - LLM as a judged
    - Automatic Evaluation Metric : BERT Score, BLUE, ROUGE-l
    - Qualitative Analysis by human


## Results

### Table 1: Automatic scores and LLM-as-a-judge across comparison methods

| Method | Upstream Evaluation | Average BERT Score-F1 |  ROUGE-L F1 | BLEU-4 | 4.1o-mini as a Judge (1-5) |
|--------|---------------------|----------------------------------|--------------------------------|-------------------------------|---------------------------------------------------|
| 1. Agentic RAG Claude 3.7 Sonnet | MRR 0.91 | 0.9186| 0.5655| 0.3941| 4.8| 
| 2. Naive RAG R1-32B-Qwen Model| MRR 0.91 |0.9120| 0.5334 | 0.3603| 4.3 |
| 3. Long Context Claude 3.7 Sonnet | - |0.8870 |0.4219 |0.2725 | 4.5| 
| 4. Claude 3.7 Sonnet  | - | 0.8797 |0.3664 |0.2184 | 3.7 | 

### Table 2: Production Metrics comparing Agentic RAG technique and Long Context Claude 3.7 Sonnet
| Method | Average Input Token (token/question) | Average Output Token (token/question) | COST ($/question) | Time (second/question) |
|--------|--------------------------------------|---------------------------------------|----------|------|
| Agentic RAG Claude 3.7 Sonnet | 9297.1 | 1529.6 | 0.05 | 23.3 |
| Long Context Claude 3.7 Sonnet| 13541.7 | 1741.2 | 0.48 | 43.2 |

## Presentation slide
[Slide Link](https://docs.google.com/presentation/d/1f0aijNcMq-LiEN8I8WaDgFDmKHLDNuGvK4xCbjN8bRA/edit?usp=sharing)


## Error Analysis


## Conclusion 

- **Technique Performance**: Table 1 shows Agentic RAG Claude 3.5 Sonnet ranks highest, followed by Naive RAG RT-32B-Qwen, Long Context Claude 3.5 Sonnet, and Claude 3.5 Sonnet alone. Both RAG implementations substantially outperformed the base model across all metrics.

- **Proprietary vs. Open-Source LLMs**: Table 1 results show no significant performance difference between proprietary and open-source LLMs in automatic metrics and human evaluation. Open-source LLMs are viable for experiments, though production deployment requires further study of latency and multi-turn memory.

- **Production Cost**: Table 2 demonstrates Agentic RAG costs 10× less per question ($0.05 vs. $0.48) with 2× faster response time (23.3 vs. 43.2 seconds) than Long Context Inference. This makes Agentic RAG more production-ready, though Long Context remains acceptable if cost optimization techniques are developed.
