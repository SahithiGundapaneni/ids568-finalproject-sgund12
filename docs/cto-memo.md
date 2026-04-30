# Memo: AI System Risk & Governance Findings
**To:** Chief Technology Officer  
**From:** Sreesahithi Gundapaneni, ML Engineering  
**Date:** April 30, 2026  
**Subject:** Production Readiness Assessment — LLM Inference API

---

## Executive Summary

Our LLM Inference API (powered by **mistral:7b-instruct** via Ollama, 4.4GB, running locally on Apple Silicon) is **conditionally ready for production** with three high-priority issues requiring attention before full-scale deployment. Two issues are addressable within one sprint; one requires a medium-term roadmap investment.

---

## Key Findings

### Finding 1: Hallucination Risk is Material (HIGH PRIORITY)
The system currently produces incorrect factual claims in approximately **26–35% of responses** containing specific numerical facts, dates, or citations. This is a fundamental property of the underlying model, not a configuration issue. Without mitigation, users receiving the system's outputs for research or decision-making tasks will encounter incorrect information with high confidence.

**Recommended Action:** Add a response disclaimer ("This information may be inaccurate — please verify with authoritative sources") before launch. Simultaneously, begin building an LLM-as-judge evaluation pipeline to flag high-risk responses for human review. Timeline: 2 weeks.

### Finding 2: Input Drift is Actively Occurring (HIGH PRIORITY)
Our monitoring data shows the distribution of user prompts has shifted significantly (+75% in average prompt length) over the past 12 weeks. This is degrading model groundedness from 0.74 to 0.65 — a **12% quality decline** that will continue without intervention.

**Recommended Action:** Trigger a model retraining cycle using the last 2,000 production samples. Additionally, implement a prompt pre-processor to break long prompts into manageable sub-questions. Timeline: 3 weeks.

### Finding 3: No PII Protection on Inference Logs (HIGH PRIORITY)
Inference request logs currently store prompt text without PII screening. If a user submits a prompt containing personal information (name, email, health data), that information persists in our logs in plaintext. This is a GDPR/CCPA compliance risk.

**Recommended Action:** Deploy PII detection on the log pipeline before accepting external user traffic. This is a one-day engineering task. Timeline: immediate.

---

## What Is Working Well

- **Monitoring infrastructure** is fully operational with real-time latency, error rate, throughput, and drift score dashboards
- **A/B testing framework** is in place and has already identified that the enhanced grounding system prompt (Model B) delivers +6.4% groundedness improvement with acceptable latency trade-off — recommend shipping Model B
- **Governance documentation** (model card, lineage diagram, risk register, audit trail) is complete and ready for compliance review
- **Reliability** is high — 96.8% success rate with no systemic failure modes identified

---

## Recommended Actions (Priority Order)

| # | Action | Owner | Timeline | Cost |
|---|---|---|---|---|
| 1 | Deploy PII detection on log pipeline | Engineering | 1 day | Low |
| 2 | Add hallucination disclaimer to all responses | Product | 2 days | None |
| 3 | Trigger model retraining with production data | ML Team | 3 weeks | Medium |
| 4 | Ship Model B (enhanced prompt) via canary rollout | Engineering | 1 week | Low |
| 5 | Implement LLM-as-judge evaluation pipeline | ML Research | 6 weeks | High |

---

## Bottom Line

With the three high-priority issues addressed, the system is safe to deploy for internal users and low-stakes external use cases. For deployment in regulated domains or high-stakes decision support, findings 1 and 3 must be fully resolved first. I recommend a phased rollout beginning with Action Items 1–4 above.

I am available to discuss any of these findings in detail.
