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
[Ollama LLM Engine]  ← llama3.2 (3B or 8B via A/B router)
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

## 2. Retrieval Risks (if RAG is added)

The current system does not include a retrieval component. However, if RAG is added in a future iteration, the following risks apply:

- **Knowledge contamination:** If the retrieval corpus contains outdated or incorrect documents, the LLM will faithfully ground its response in wrong information
- **Stale knowledge:** Documents added once and never updated create a time-decay problem (particularly for regulatory or policy documents)
- **Exposure risk:** If the retrieval corpus contains confidential documents, prompt injection could cause the LLM to reveal them

**Mitigation for future RAG:** Implement corpus freshness timestamps; exclude documents older than 90 days from retrieval; restrict corpus to approved sources only.

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
