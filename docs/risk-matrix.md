# Risk Matrix — LLM Inference API
**IDS 568 Final Project · Sreesahithi Gundapaneni (sgund12)**

---

## Likelihood × Severity Matrix

| Risk | Likelihood (1–5) | Severity (1–5) | Score | Priority | Mitigation |
|---|---|---|---|---|---|
| Hallucinated numerical facts in output | 5 | 4 | **20** | 🔴 Critical | Groundedness monitoring; output disclaimer |
| Prompt injection attack via user input | 3 | 5 | **15** | 🔴 Critical | Input sanitisation; system prompt hardening |
| PII exposure in inference logs | 3 | 5 | **15** | 🔴 Critical | Anonymise logs; encrypt at rest |
| Knowledge cutoff staleness causing wrong answers | 5 | 3 | **15** | 🔴 High | Timestamp responses; add RAG for recent data |
| Input drift degrading model accuracy | 4 | 3 | **12** | 🔴 High | Drift monitoring (C4); retraining pipeline |
| Gender/racial bias in outputs | 3 | 4 | **12** | 🔴 High | Monthly bias audit; bias-mitigation system prompt |
| P99 latency spikes breaching SLA | 3 | 3 | **9** | 🟡 Medium | Request queue; separate heavy/light lanes |
| Model serving infrastructure downtime | 2 | 4 | **8** | 🟡 Medium | Health check endpoint; restart-on-failure policy |
| Quantization artefacts in long responses | 2 | 3 | **6** | 🟡 Medium | Max token cap at 512; monitor token distribution |
| Non-English query degradation | 4 | 2 | **8** | 🟡 Medium | Language detection; route to multilingual model |
| Audit trail gaps during rapid deployments | 2 | 3 | **6** | 🟡 Medium | Automated version logging in CI/CD pipeline |
| Usage for prohibited domains (medical/legal) | 2 | 5 | **10** | 🔴 High | Explicit policy; output classifier for domain detection |

---

## Visual Risk Matrix

```
SEVERITY →    1-Trivial  2-Minor  3-Moderate  4-Major  5-Critical
LIKELIHOOD ↓
5-Almost      ·          ·        [Staleness]  [Halluc] ·
  certain                         [Drift]
4-Likely      ·          [Lang]   ·            ·        ·
3-Possible    ·          ·        [Latency]    [Bias]   [Injection]
                                  [Quant]      [Audit]  [PII]
                                               [Domain]
2-Unlikely    ·          ·        ·            [Infra]  ·
1-Rare        ·          ·        ·            ·        ·
```

---

## Top 3 Risks — Detailed Mitigation Plans

### 1. Hallucinated Numerical Facts (Score: 20)
- **Detection:** Groundedness score monitoring triggers alert when mean drops below 0.68
- **Response:** Engineering review of prompt template; add explicit instruction to say "I don't know" for uncertain facts
- **Long-term:** Implement LLM-as-judge pipeline to score individual response factuality

### 2. Prompt Injection (Score: 15)
- **Detection:** Input validator checks for common injection patterns (e.g. "ignore previous instructions", role-play overrides)
- **Response:** Reject flagged requests with HTTP 400; log for security review
- **Long-term:** Red-team testing quarterly; system prompt includes explicit injection resistance instructions

### 3. PII in Logs (Score: 15)
- **Detection:** PII scanner (regex + NER) runs on prompt before logging
- **Response:** Hash or redact detected PII tokens; alert security team if >10 PII instances in 1 hour
- **Long-term:** End-to-end encryption of log pipeline; annual privacy audit
