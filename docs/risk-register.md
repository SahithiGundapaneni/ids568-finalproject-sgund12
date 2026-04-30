# Risk Register — LLM Inference API
**IDS 568 Final Project · Sreesahithi Gundapaneni (sgund12)**

---

## Risk Categories: Bias · Robustness · Privacy · Compliance

| ID | Category | Risk Description | Likelihood | Severity | Risk Score | Mitigation |
|---|---|---|---|---|---|---|
| R-01 | Bias | Model outputs reflect gender or racial stereotypes from training data | Medium | High | 🔴 High | Monthly bias audit on 100-sample outputs; add system prompt to discourage stereotyping |
| R-02 | Bias | Non-English queries produce lower quality, biased responses | High | Medium | 🔴 High | Add language detection; route non-English queries to multilingual model variant |
| R-03 | Bias | Model performs worse on domain-specific jargon outside training distribution | High | Medium | 🔴 High | Collect domain-specific examples; fine-tune or RAG-augment for target domains |
| R-04 | Robustness | Prompt injection attacks hijack model behaviour via malicious user input | Medium | Critical | 🔴 Critical | Input sanitisation; system prompt hardening; output content filtering |
| R-05 | Robustness | Model produces confident hallucinations for out-of-knowledge queries | High | High | 🔴 High | Groundedness monitoring (C1); output disclaimer for factual claims |
| R-06 | Robustness | P99 latency spikes cause timeout cascades affecting all concurrent users | Medium | High | 🔴 High | Request queue with timeout; separate heavy/light request lanes |
| R-07 | Robustness | Quantization artefacts cause incoherent responses on long outputs | Low | Medium | 🟡 Medium | Monitor token distribution (C1); cap max response tokens at 512 |
| R-08 | Privacy | Model may reproduce memorised PII from training data | Low | Critical | 🔴 High | PII detection in output; block/redact identified PII before returning |
| R-09 | Privacy | Inference logs may capture sensitive user prompt data | Medium | High | 🔴 High | Anonymise prompt logs; 30-day log retention policy; encrypt at rest |
| R-10 | Compliance | Outputs may be used to produce misleading content in regulated domains | Medium | High | 🔴 High | Usage policy enforcement; domain restriction (no medical/legal advice) |
| R-11 | Compliance | No audit trail for model version changes in production | Low | Medium | 🟡 Medium | Structured audit trail in `logs/audit-trail.json` (see C3) |
| R-12 | Compliance | Model knowledge cutoff creates staleness risk for time-sensitive queries | High | Medium | 🔴 High | Timestamp all responses with knowledge cutoff date; add RAG for recent data |
| R-13 | Robustness | mistral:7b-instruct misinterprets technical acronyms (e.g. "RAG" as "Reward-Adequate Goal-based") without sufficient prompt context | High | High | 🔴 High | Add acronym disambiguation to system prompt; validate outputs against known terminology |
| R-14 | Robustness | Agent reasoning fields empty or show JSON fallback in agentic pipelines | High | Medium | 🔴 High | Enforce structured output schema; validate reasoning field is non-empty before returning response |

---

## Risk Matrix Summary

```
SEVERITY →      Low        Medium      High       Critical
LIKELIHOOD ↓
High         🟢 Low     🔴 High    🔴 High    🔴 Critical
Medium       🟢 Low     🟡 Med     🔴 High    🔴 Critical  
Low          🟢 Low     🟡 Med     🟡 Med     🔴 High
```

**Highest priority risks (address immediately):** R-04, R-05, R-08, R-12

---

## Residual Risk After Mitigations

After implementing all mitigations above, the residual risk profile reduces to:
- 2 High risks (R-01, R-06) — ongoing monitoring required
- 6 Medium risks — quarterly review cadence
- 4 Low risks — annual review sufficient
