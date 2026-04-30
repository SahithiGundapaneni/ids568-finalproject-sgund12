# Drift Diagnostic Report
**IDS 568 Final Project · Sreesahithi Gundapaneni (sgund12)**  
**Analysis Window:** Reference (historical, n=1,000) vs Production (recent, n=1,000)  
**Date:** April 30, 2026

---

## Executive Summary

Significant input distribution drift was detected across three of four monitored features. The most severe drift is in **prompt length** (PSI = 0.52), indicating a fundamental shift in how users are interacting with the system. This drift is estimated to cause an **8–12% accuracy degradation** and an increase in hallucination rate. **Immediate retraining is recommended.**

---

## 1. Which Features Drifted Most?

| Feature | PSI | Status | Mean (Ref) | Mean (Prod) | Shift |
|---|---|---|---|---|---|
| `prompt_length` | **0.52** | 🚨 DRIFTED | 200 chars | 350 chars | +75% |
| `response_tokens` | **0.41** | 🚨 DRIFTED | 175 tokens | 280 tokens | +60% |
| `groundedness` | **0.24** | 🚨 DRIFTED | 0.74 | 0.65 | −12% |
| `latency_s` | **0.08** | ✅ STABLE | 0.48s | 0.56s | +17% |

PSI interpretation: < 0.10 = stable, 0.10–0.20 = monitor, > 0.20 = significant drift

**Anomaly detection (IQR-based):**
- `prompt_length`: 86 anomalous requests (8.6%) — far outside historical norms
- `response_tokens`: 56 anomalous requests (5.6%)
- `latency_s`: 7 anomalous requests (0.7%) — acceptable
- `groundedness`: 0 anomalies — distribution shifted but no extreme outliers

---

## 2. Impact on Model Performance

### Accuracy / Groundedness Impact
The groundedness score dropped from 0.74 (reference) to 0.65 (production) — a **−12% relative decline**. This is the most operationally significant finding. The root cause is the 75% increase in prompt length: the model was calibrated on prompts of ~200 characters (short factual questions), but production prompts now average 350 characters (document summarisation and multi-part questions).

Longer, more complex prompts are outside the model's optimal operating range for the current configuration, leading to:
- More hallucinated claims in responses
- Responses that address only part of complex multi-part questions
- Factual accuracy declining on domain-specific extended queries

### Latency Impact
While PSI for latency is stable (0.08), the mean latency increased by +17%. This is attributable to the longer responses (60% more tokens). At current throughput (85 rpm), this is within SLA, but under peak load the compounding effect of longer prompts + longer responses creates a risk of SLA breaches.

### Downstream Business Impact
- Approximately **1 in 8 responses** that were previously grounded are now incorrectly grounded
- If the system is used for customer-facing Q&A, this translates to a measurable increase in user-reported inaccurate answers
- If left unaddressed for 4 weeks, the PSI trend analysis suggests drift will reach PSI = 0.70+ on prompt_length, making the model increasingly unreliable

---

## 3. Retraining and Intervention Recommendations

### Immediate (within 1 week)
1. **Trigger retraining pipeline** with the most recent 2,000 production samples, weighted toward the new longer-prompt distribution
2. **Add a prompt pre-processor** that breaks long prompts (>300 chars) into sub-questions and aggregates answers — this reduces the effective input complexity without retraining
3. **Raise the groundedness alert threshold** in the monitoring dashboard from 0.65 to 0.70 to catch further degradation early

### Short-term (within 1 month)
4. **Fine-tune on domain-specific long-prompt examples** if the document Q&A use case is intended to continue growing
5. **Implement RAG augmentation** to provide the model with retrieved context, reducing hallucination risk for longer queries

### Monitoring
6. **Set weekly PSI checkpoints** — if `prompt_length` PSI exceeds 0.60 or `groundedness` mean drops below 0.60, escalate to on-call ML engineer
7. **Connect drift triggers to audit trail** — each PSI threshold breach should be logged in `logs/audit-trail.json` with timestamp and recommended action

---

## 4. Connection to Other Components

- The drift detected here validates the **drift score alert** implemented in Component 1 (monitoring dashboard) — the dashboard drift score would have fired a warning alert at ~week 7 of the PSI-over-time analysis
- The groundedness drop to 0.65 narrows the quality advantage of Model B identified in Component 2 — if drift continues, even the larger model may not maintain its quality edge without retraining
- This drift analysis directly informs Risk R-03 and R-05 in the Component 3 risk register
