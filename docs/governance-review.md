# Governance Review — AI System Risk Assessment
**IDS 568 Final Project · Sreesahithi Gundapaneni (sgund12)**  
**System:** LLM Inference API (Ollama + FastAPI)  
**Date:** April 30, 2026

---

## System Boundary

See `docs/system-boundary-diagram.png` for the visual diagram.

```
[User Request]
     │
     ▼
[Input Validator]  ← checks: length, PII, injection patterns
     │
     ▼
[FastAPI Wrapper]  ← rate limiting, auth, request logging
     │
     ▼
[Ollama LLM Engine]  ← mistral:7b-instruct (A/B router selects prompt variant)
     │
     ▼
[Output Filter]  ← PII detection, content safety check
     │
     ▼
[Response + Metrics Emission]  ← Prometheus metrics → Dashboard
     │
     ▼
[User Response]
```

---

## 1. Data Security

**Data flow:** User prompts arrive via HTTP, are processed in-memory by the LLM, and responses are returned. No prompt data is persisted to disk except in anonymised log form.

**Key controls:**
- All API endpoints require authentication (API key header)
- Inference runs locally — no data leaves the host machine to external LLM APIs
- Log files are anonymised (prompt content hashed, not stored in plaintext)
- 30-day log retention policy; automatic deletion after expiry

**Gap:** Currently no encryption at rest for log files. Recommendation: implement AES-256 encryption for `logs/` directory.

---

## 2. Retrieval Risks (RAG Pipeline — from Milestone 6)

This system was extended in Milestone 6 with a RAG pipeline and agentic controller. The following retrieval risks apply to that architecture and inform the current governance posture:

- **Knowledge contamination:** If the retrieval corpus contains outdated or incorrect documents, mistral:7b-instruct will faithfully ground its response in wrong information with high confidence.
- **Stale knowledge:** Documents added once and never updated create a time-decay problem (particularly for regulatory or policy documents). A 90-day freshness policy is recommended.
- **Exposure risk:** If the retrieval corpus contains confidential documents, prompt injection could cause the LLM to reveal them verbatim in responses.
- **Acronym misinterpretation in retrieval context:** mistral:7b-instruct has demonstrated misinterpreting technical acronyms (e.g. "RAG" as "Reward-Adequate Goal-based") when retrieval context is absent or ambiguous. This is an active risk in any RAG-augmented deployment.
- **Agent reasoning quality:** In agentic pipelines, the model frequently produces empty reasoning fields or JSON fallback traces rather than substantive chain-of-thought. This reduces auditability of agent decisions.

**Mitigations:** Corpus freshness timestamps; approved-source allowlist; acronym disambiguation in system prompt; structured reasoning enforcement via output schema validation.

---

## 3. Hallucination Risk Points

| System Stage | Hallucination Risk | Severity |
|---|---|---|
| Input: short/vague prompts | Model fills gaps with plausible fiction | Medium |
| Input: prompts about events post-cutoff | Model invents plausible but false recent facts | High |
| Input: domain-specific jargon | Model confidently misapplies terminology | High |
| Output: numerical claims (dates, statistics) | Model fabricates specific numbers | Critical |
| Output: citations / references | Model invents plausible-sounding source names | Critical |

**Current mitigation:** Groundedness monitoring in Component 1 catches aggregate drift. Individual response-level hallucination detection requires a separate LLM-as-judge pipeline (future work).

---

## 4. Tool-Misuse Pathways

The current system is not agentic (no tool use). If tool use is added:

- **Code execution tools:** Could be misused to run arbitrary code via prompt injection
- **Web search tools:** Could be directed to retrieve harmful content
- **File system tools:** Could leak confidential files via path traversal in prompts

**Mitigation:** Implement tool allowlists; sandbox all tool execution; log all tool invocations.

---

## 5. Compliance Concerns

| Concern | Status | Mitigation |
|---|---|---|
| PII in prompts (GDPR/CCPA) | ⚠️ Risk | Input PII detector; no plaintext log storage |
| Outputs used for regulated decisions | ⚠️ Risk | Usage policy; disclaimer on all responses |
| Model bias in hiring/lending decisions | ❌ Out of scope | Explicitly prohibited in usage policy |
| Audit trail for model changes | ✅ Implemented | See `logs/audit-trail.json` |
| Data retention limits | ⚠️ Partial | 30-day policy defined; enforcement not automated |
