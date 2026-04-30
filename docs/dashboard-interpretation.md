# Dashboard Interpretation — LLM Inference API
**IDS 568 Final Project · Sreesahithi Gundapaneni (sgund12)**

---

## 1. What Does the Dashboard Reveal About System Health?

The monitoring dashboard instruments a local LLM inference API (backed by Ollama) across seven panels covering latency, throughput, error rate, token distribution, drift score, and input characteristics. The 120-second simulation window represents a microcosm of production traffic at ~1.5 requests/second.

**Overall health: ACCEPTABLE with two watchpoints.**

### Panel-by-Panel Interpretation

**① Request Latency (P50 / P99)**
The P50 latency holds steady at approximately 0.45–0.55 seconds, which is within the 1-second SLA for interactive use. However, P99 latency shows two distinct spikes — at t=40s (+2.8s) and t=85s (+3.1s) — that both exceed the 2-second alert threshold. These spikes indicate that roughly 1% of requests experience severe degradation, likely caused by:
- GPU memory pressure during concurrent large-prompt requests
- Ollama model loading overhead when the KV cache is evicted

**② Live KPIs**
The summary panel shows average P99 latency near 1.4 seconds, which is below the alert threshold on average but masks the spike behaviour visible in Panel ①. This demonstrates why summary statistics alone are insufficient — tail latency must be monitored separately.

**③ Throughput (req/min)**
Throughput averages ~85 req/min and dips to ~55 req/min during both latency spike windows. This anti-correlation confirms the spikes are not load-related (more traffic causing slowness) but rather resource-contention events at the model level.

**④ Error Rate**
The rolling error rate stays near 2.5% during normal operation but spikes to ~8.5% and ~7% during the two latency events. A 5% error threshold would fire an alert during both incidents, enabling on-call engineers to investigate within minutes.

**⑤ Response Token Distribution**
The bimodal token distribution (peak at ~175 tokens, secondary peak at ~420 tokens) reveals two usage modes: quick factual queries and longer document-summarisation requests. The longer requests correlate with the latency spikes. A separate monitoring lane per request class would improve diagnostic resolution.

**⑥ Drift Score**
The drift score rises steadily from 0.12 to ~0.50 over the 120-second window. This gradual increase suggests the input distribution is shifting — consistent with new user segments sending longer, more complex prompts. The score crosses the **warning threshold (0.30)** at approximately t=65s and approaches but does not breach the **critical threshold (0.45)** by the end of the window.

**⑦ Input Prompt Length**
Prompt lengths are approximately normally distributed around 200 characters. The absence of multi-modal peaks here (unlike token output) suggests the drift is behavioural — users are asking more complex questions rather than changing topic domain.

---

## 2. Bottlenecks and Risks

| Observation | Root Cause | Severity |
|---|---|---|
| P99 latency spikes >2s at t=40 and t=85 | GPU KV-cache eviction / memory contention | HIGH |
| Error rate spikes to 8.5% | Timeout cascade during memory pressure events | HIGH |
| Drift score trending toward critical (0.45) | Shifting user population / new use-cases | MEDIUM |
| Bimodal token distribution | Two distinct query classes sharing one serving config | MEDIUM |
| Throughput dips to 55 rpm | Head-of-line blocking from slow requests | LOW-MEDIUM |

**Primary bottleneck:** The serving infrastructure does not isolate heavy (long-prompt, long-response) requests from light ones. A single slow request holding a GPU thread causes latency spikes for all concurrent requests.

---

## 3. Alert Trigger Conditions for Production

The following alert rules are defined in `dashboards/prometheus.yml`:

| Alert Name | Condition | Severity | Action |
|---|---|---|---|
| `HighP99Latency` | P99 latency > 2.0s for 2+ minutes | WARNING | Page on-call SRE |
| `CriticalLatency` | P99 latency > 5.0s for 1+ minute | CRITICAL | Auto-scale + page |
| `HighErrorRate` | Error rate > 5% over 1-minute window | WARNING | Page on-call SRE |
| `ThroughputDrop` | Throughput < 60 rpm for 3+ minutes | WARNING | Investigate load balancer |
| `DriftWarning` | Drift score > 0.30 for 5+ minutes | INFO | Notify ML team |
| `DriftCritical` | Drift score > 0.45 for 2+ minutes | WARNING | Trigger retraining pipeline |

**Design justification:** Alert thresholds were set at 2× the normal operating range to minimise false positives while ensuring real incidents are caught within two minutes. The 2-minute sustain window for latency alerts prevents pager fatigue from transient spikes that self-resolve.

---

## 4. Design Choices

The monitoring stack uses **`prometheus_client` (Python)** for metric emission rather than OpenTelemetry because:
1. Zero external infrastructure required for local development
2. Prometheus metrics format is industry-standard and readily exported to Grafana
3. The library supports all required metric types: Counter, Histogram, Gauge

The seven-panel layout was designed to support progressive drill-down: KPI summary → trend panels → distribution panels → drift panel. This mirrors how an on-call engineer would triage an incident.
