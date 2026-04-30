# Model Card — LLM Inference API (Ollama / mistral:7b-instruct)
**IDS 568 Final Project · Sreesahithi Gundapaneni (sgund12)**  
**Model Version:** v1.0 (mistral:7b-instruct, default system prompt) / v1.1 (mistral:7b-instruct, enhanced grounding system prompt)  
**Last Updated:** April 30, 2026

---

## Model Details

| Field | Value |
|---|---|
| Model Family | Mistral 7B Instruct (Mistral AI) |
| Model ID | mistral:7b-instruct (via Ollama, ID: 6577803aa9a0) |
| Parameter Count | 7 billion |
| Serving Framework | Ollama (local inference) + FastAPI wrapper |
| Quantization | Q4_K_M (4-bit, GGUF format, 4.4 GB on disk) |
| Hardware | Apple Silicon MacBook (Metal GPU backend) |
| Inference Mode | Single-turn instruction-following Q&A |
| Primary Use Case | General-purpose factual question answering |

---

## Intended Use

**In-scope applications:**
- Factual Q&A on general knowledge topics
- Summarisation of provided text passages
- Code explanation (not code generation for production)
- Educational tutoring assistance

**Out-of-scope applications:**
- Medical diagnosis or clinical decision support
- Legal advice or contract interpretation
- Real-time financial trading decisions
- Safety-critical systems (autonomous vehicles, industrial control)
- Generation of content intended for deception or manipulation

---

## Performance Metrics

Evaluated on a simulated production dataset (n=1,000 requests):

| Metric | Baseline (mistral:7b-instruct v1.0) | Challenger (mistral:7b-instruct v1.1) |
|---|---|---|
| Groundedness Score (mean) | 0.720 | 0.784 |
| Inference Latency P50 | 0.45s | 0.78s |
| Inference Latency P99 | 1.8s | 2.4s |
| Success Rate | 96.8% | 96.4% |
| Mean Response Tokens | 175 | 205 |

*Groundedness is measured as the proportion of factual claims in the response that are supported by the input context or verified knowledge.*

---

## Training Data Description

Mistral 7B Instruct was trained by Mistral AI on a large corpus of publicly available text data including web pages, books, and code. Key characteristics:
- Architecture: Transformer with Grouped Query Attention (GQA) and Sliding Window Attention (SWA)
- Knowledge cutoff: approximately early 2024
- Language: primarily English, with multilingual capability
- Fine-tuned for instruction following using supervised fine-tuning (SFT)
- No additional fine-tuning was applied in this project; base Ollama weights used as-is

---

## Limitations and Failure Modes

1. **Knowledge staleness:** The model has no knowledge of events after its training cutoff (~early 2024). Queries about recent events will produce outdated or hallucinated answers.
2. **Prompt length sensitivity:** Performance degrades noticeably for prompts exceeding 1,500 characters. Drift detection shows this is an active production risk.
3. **Hallucination on specifics:** The model will confidently generate plausible-sounding but incorrect numerical facts, dates, and citations.
4. **Acronym and terminology misinterpretation:** mistral:7b-instruct has been observed misinterpreting domain acronyms — for example, interpreting "RAG" as "Reward-Adequate Goal-based" rather than "Retrieval-Augmented Generation" in agentic contexts. This is a known failure mode when technical acronyms appear without sufficient context in the prompt.
5. **Language bias:** Non-English queries produce substantially lower groundedness scores (~0.55 vs 0.72 for English).
6. **Quantization artefacts:** Q4 quantization introduces occasional incoherence in long responses (>500 tokens).
7. **No refusal mechanism:** The baseline model does not reliably refuse harmful or out-of-scope requests without a system prompt guardrail.
8. **Agent reasoning gaps:** When used in agentic pipelines, the model frequently produces empty reasoning fields or falls back to JSON formatting errors rather than substantive chain-of-thought output.

---

## Ethical Risks and Considerations

| Risk | Description | Mitigation |
|---|---|---|
| Misinformation | Model may state incorrect facts confidently | Groundedness monitoring; user disclaimers |
| Bias amplification | Training data may encode societal biases | Regular bias audits on output samples |
| Privacy leakage | Model may reproduce memorised training data | No PII in prompts (enforced by input validator) |
| Misuse for manipulation | Capable of generating persuasive false content | Usage policy; rate limiting; logging |

---

## Lineage Summary

See `docs/lineage-diagram.png` for the full lineage diagram.

```
Public Web Data → Mistral AI Pre-training → GGUF Q4 Quantization
→ Ollama Local Serving (mistral:7b-instruct) → FastAPI Wrapper
→ Production Monitoring (C1) → A/B Testing (C2)
→ Drift Detection (C4) → Risk Assessment (C5)
```
